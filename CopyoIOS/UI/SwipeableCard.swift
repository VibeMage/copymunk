import SwiftUI

/// 左滑删除（红）/ 右滑固定（蓝）。
///
/// 瀑布流不是 List，`swipeActions` 用不了，只能自己接手势。关键是只在**水平方向明显占优**时才接管，
/// 否则纵向滚动会被吃掉——两列卡片本来就窄，横向误判非常明显。
///
/// 手势用 UIKit 的 `UIPanGestureRecognizer`（`HorizontalPan`），不用 SwiftUI 的 `DragGesture`：
/// 卡片在 ScrollView 里，iOS 18 起滚动视图的拖动会先把触摸拿走，`.gesture(DragGesture())` 根本收不到事件，
/// 1.1.0 上线后左右滑就是这样整个失灵的（`SwipeCardTests` 能复现）。UIKit 那边可以在
/// `gestureRecognizerShouldBegin` 里按起手速度判方向：横向才开始，纵向直接失败、交给滚动。
struct SwipeableCard<Content: View>: View {
    var onDelete: (() -> Void)?
    var onPin: (() -> Void)?
    /// 已经固定过的条目不再提供右滑固定
    var pinEnabled: Bool = true
    @ViewBuilder var content: () -> Content

    /// 全滑阈值：越过就直接执行，不停在半开状态（设计稿的位移量）
    private let actionThreshold: CGFloat = 96

    /// 24 不在系统文本样式的默认点数上（title2 是 22、title 是 28），按 title2 缩；
    /// 下面那行 12 正好是 `caption`，两者一起跟随辅助功能字号长大。
    @ScaledMetric(relativeTo: .title2) private var actionSymbolSize: CGFloat = 24

    @State private var offset: CGFloat = 0
    @Environment(\.layoutDirection) private var layoutDirection

    var body: some View {
        ZStack {
            actionLayer
            content()
                .offset(x: offset)
                .gesture(HorizontalPan(onChanged: dragChanged, onEnded: dragEnded))
                // 左右滑是一条裸 `DragGesture`，旁白用户根本做不出这个手势——
                // 不补这两条具名动作，删除与固定对他们就只存在于「被包的内容恰好也提供了菜单」里。
                //
                // 挂在 `content()` 上而不是外面那个 ZStack 上：卡片是一个合成的无障碍元素，
                // 挂在它自己身上才一定落到那个停留点。
                //
                // 「删除」「固定」这两条具名动作**归这一层所有**：手势是它的，名字也该是它的。
                // 被包的内容不要再给同名动作——两层合成的是同一个停留点，重一条的效果是
                // 转子里连着念两次「删除」，名字一样、落点不同，旁白用户无从分辨。
                // （`HistoryCardView` 因此不给「删除」，它那边的注释也写了归属在这里。）
                .accessibilityActions { swipeActions }
        }
    }

    @ViewBuilder
    private var swipeActions: some View {
        if let onDelete {
            Button(String(localized: "Delete"), action: onDelete)
        }
        if pinEnabled, let onPin {
            Button(String(localized: "Pin"), action: onPin)
        }
    }

    private var actionLayer: some View {
        ZStack {
            if offset < 0 {
                HStack {
                    Spacer()
                    actionLabel(symbol: "trash", title: String(localized: "Delete"))
                        .padding(.trailing, 22)
                }
                .background(CopyoTheme.destructive)
            } else if offset > 0 {
                HStack {
                    actionLabel(symbol: "pin", title: String(localized: "Pin"))
                        .padding(.leading, 22)
                    Spacer()
                }
                .background(CopyoTheme.accent)
            }
        }
        .clipShape(RoundedRectangle(cornerRadius: CopyoTheme.Radius.card, style: .continuous))
        // 这一层只是卡片滑开后露出的底色，语义由上面两条具名动作承担；
        // 不藏起来旁白会在「删除」「固定」两个装饰标签上白停一次
        .accessibilityHidden(true)
    }

    private func actionLabel(symbol: String, title: String) -> some View {
        VStack(spacing: 2) {
            Image(systemName: symbol)
                .font(.system(size: actionSymbolSize, weight: .semibold))
            Text(title)
                .font(.system(.caption, weight: .semibold))
        }
        .foregroundStyle(.white)
    }

    /// 越过阈值后加阻尼，手感上告诉用户「已经到位了」
    private func damped(_ translation: CGFloat) -> CGFloat {
        let magnitude = abs(translation)
        guard magnitude > actionThreshold else { return translation }
        let excess = (magnitude - actionThreshold) * 0.25
        return translation < 0 ? -(actionThreshold + excess) : actionThreshold + excess
    }

    private func dragChanged(_ translationX: CGFloat) {
        // UIKit 给的是屏幕上的物理位移，SwiftUI 的 offset 在 RTL 下却按逻辑方向镜像（+x 往左）。
        // 换成逻辑方向，卡片才跟着手指走；RTL 下随之变成左滑固定、右滑删除，与系统列表的镜像习惯一致
        var translation = layoutDirection == .rightToLeft ? -translationX : translationX
        if translation > 0 && (!pinEnabled || onPin == nil) { translation = 0 }
        if translation < 0 && onDelete == nil { translation = 0 }
        offset = damped(translation)
    }

    private func dragEnded() {
        let finished = offset
        withAnimation(CopyoTheme.springAnimation) { offset = 0 }
        if finished <= -actionThreshold, let onDelete {
            onDelete()
        } else if finished >= actionThreshold, pinEnabled, let onPin {
            onPin()
        }
    }
}

/// 只认横向的拖动。起手时水平速度要明显大于垂直速度才开始，否则直接失败，
/// 外面的 ScrollView 照常纵向滚动；开始之后会取消卡片上的点按，不会滑完还顺带复制一次。
private struct HorizontalPan: UIGestureRecognizerRepresentable {
    var onChanged: (CGFloat) -> Void
    var onEnded: () -> Void

    func makeUIGestureRecognizer(context: Context) -> UIPanGestureRecognizer {
        let pan = UIPanGestureRecognizer()
        pan.delegate = context.coordinator
        return pan
    }

    func handleUIGestureRecognizerAction(_ recognizer: UIPanGestureRecognizer, context: Context) {
        switch recognizer.state {
        case .began, .changed:
            onChanged(recognizer.translation(in: recognizer.view).x)
        case .ended, .cancelled, .failed:
            onEnded()
        default:
            break
        }
    }

    func makeCoordinator(converter: CoordinateSpaceConverter) -> Coordinator {
        Coordinator()
    }

    final class Coordinator: NSObject, UIGestureRecognizerDelegate {
        func gestureRecognizerShouldBegin(_ gestureRecognizer: UIGestureRecognizer) -> Bool {
            guard let pan = gestureRecognizer as? UIPanGestureRecognizer else { return false }
            let velocity = pan.velocity(in: pan.view)
            return abs(velocity.x) > abs(velocity.y) * 1.5
        }
    }
}
