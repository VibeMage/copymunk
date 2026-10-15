import SwiftUI

/// 分享面板标题旁那枚 26pt 应用标记（design-spec 3.10）。
///
/// 设计稿这里放的是 App 图标本身。扩展 bundle 里没有 App 图标，跨进程取自己的图标也没有公开 API，
/// 所以把 `AppIcon.png` 缩成 52 / 78px 放进 `ShareAssets.xcassets/AppMark`，主应用与分享扩展都打包这一份
/// （Mac 目标在工程的例外表里排除了它）。换图标时记得重新缩一遍：
///
///     sips -z 52 52 CopyoIOS/Assets.xcassets/AppIcon.appiconset/AppIcon.png \
///         --out CopyoShared/ShareAssets.xcassets/AppMark.imageset/AppMark@2x.png   # 3x 用 78
///
/// 改名 Copymunk 之前这里是照旧图标构图手画的红蓝卡片，换了图标就对不上了。
struct CopyoMark: View {
    /// 标记的边长。design-spec 3.10 给的是 26；这是图形不是字，所以不跟随动态字体。
    var size: CGFloat = 26

    var body: some View {
        // 图标是满版方图，圆角照主屏幕的比例切
        let shape = RoundedRectangle(cornerRadius: size * 0.2237, style: .continuous)
        Image("AppMark")
            .resizable()
            .interpolation(.high)
            .frame(width: size, height: size)
            .clipShape(shape)
            // 深色 sheet（#1C1C1E）上深底会与面板糊在一起，补一圈极细的描边把方块轮廓勾出来
            .overlay { shape.strokeBorder(Color.primary.opacity(0.12), lineWidth: 0.5) }
            // 纯装饰：它旁边就是「保存到 Copymunk」，读屏再念一遍品牌标记只会多一个停留点
            .accessibilityHidden(true)
    }
}
