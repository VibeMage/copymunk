import XCTest

/// 历史卡片的左滑删除 / 右滑固定（`SwipeableCard`）。
/// 用 `-demoData` 的内存样例库跑，不碰真实数据；英文界面，标签按 `ClipCard.accessibilityDescription` 找。
final class SwipeCardTests: XCTestCase {
    private let app = XCUIApplication()

    override func setUp() {
        continueAfterFailure = false
        app.launchArguments = ["-demoData", "-skipOnboarding", "-localOnly", "-demoTheme", "light",
                               "-AppleLanguages", "(en)", "-AppleLocale", "en_US"]
        app.launch()
    }

    /// 卡片是按钮（合成的无障碍元素）。别用 `.any`：外层容器的标签也可能带着这段文字，
    /// 拖动会落在容器中点——屏幕底部，触发的是系统切换 App 的手势
    /// 样例库里同一段文字可能有好几张卡（瀑布流下面还有），取屏幕上点得到的那张：
    /// 屏幕外的卡坐标会被压到屏幕底边，横拖就成了系统切换 App 的手势
    private func card(containing text: String) -> XCUIElement {
        let query = app.buttons.matching(NSPredicate(format: "label CONTAINS %@", text))
        _ = query.firstMatch.waitForExistence(timeout: 10)
        return query.allElementsBoundByIndex.first { $0.isHittable } ?? query.firstMatch
    }

    /// 横向拖固定的距离。`swipeLeft()` 只拖半张卡宽，窄列里不到 96pt 的执行阈值。
    /// 像手指一样偏向另一侧起手，但别贴着屏幕边缘——右列卡片的最右边一碰就是系统的边缘手势
    private func drag(_ element: XCUIElement, by dx: CGFloat) {
        let start = element.coordinate(withNormalizedOffset: CGVector(dx: dx < 0 ? 0.7 : 0.3, dy: 0.5))
        start.press(forDuration: 0.05, thenDragTo: start.withOffset(CGVector(dx: dx, dy: 0)))
    }

    /// 1.1.0 的回归：卡片上的横滑手势把纵向滚动也吃掉了，整个历史列表上下滑不动
    func testListScrollsVertically() {
        let first = card(containing: "verification code is 482913")
        XCTAssertTrue(first.waitForExistence(timeout: 10))
        let before = first.frame.minY
        let start = first.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.5))
        start.press(forDuration: 0.05, thenDragTo: start.withOffset(CGVector(dx: 0, dy: -300)))
        sleep(1)
        XCTAssertLessThan(first.frame.minY, before - 100, "从卡片上往上拖，列表应该往上滚")
    }

    func testSwipeLeftDeletes() {
        let text = "Q4 roadmap Friday 3pm"
        let card = card(containing: text)
        XCTAssertTrue(card.waitForExistence(timeout: 10))
        // 同一段文字有好几张卡，按数量判断少了一张
        let matches = app.buttons.matching(NSPredicate(format: "label CONTAINS %@", text))
        let before = matches.count
        drag(card, by: -150)
        let deleted = NSPredicate { _, _ in matches.count == before - 1 }
        wait(for: [expectation(for: deleted, evaluatedWith: nil)], timeout: 3)
    }

    func testSwipeRightPins() {
        let card = card(containing: "verification code is 482913")
        XCTAssertTrue(card.waitForExistence(timeout: 10))
        XCTAssertFalse(card.label.contains("Pinned"))
        drag(card, by: 150)
        let pinned = app.buttons
            .matching(NSPredicate(format: "label CONTAINS %@ AND label CONTAINS %@", "verification code is 482913", "Pinned"))
            .firstMatch
        XCTAssertTrue(pinned.waitForExistence(timeout: 3), "右滑后卡片应被固定到默认 Pinboard")
    }
}
