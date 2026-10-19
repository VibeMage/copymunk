import XCTest

/// 历史卡片长按菜单里的「预览」与「打开详情」：触屏上仅有的两个入口
/// （空格只在接了硬件键盘时有，轻点是复制，点菜单上方放大的预览卡片只会收起菜单）。
/// 用 `-demoData` 的内存样例库跑，不碰真实数据；英文界面。
final class CardMenuTests: XCTestCase {
    private let app = XCUIApplication()
    private let text = "verification code is 482913"

    override func setUp() {
        continueAfterFailure = false
        app.launchArguments = ["-demoData", "-skipOnboarding", "-localOnly", "-demoTheme", "light",
                               "-AppleLanguages", "(en)", "-AppleLocale", "en_US"]
        app.launch()
    }

    /// 与 `SwipeCardTests` 同一个找法：取屏幕上点得到的那张
    private func longPressCard() {
        let query = app.buttons.matching(NSPredicate(format: "label CONTAINS %@", text))
        XCTAssertTrue(query.firstMatch.waitForExistence(timeout: 10))
        let card = query.allElementsBoundByIndex.first { $0.isHittable } ?? query.firstMatch
        card.press(forDuration: 1.2)
    }

    func testPreviewFromMenu() {
        longPressCard()
        let preview = app.buttons["Preview"]
        XCTAssertTrue(preview.waitForExistence(timeout: 3), "长按菜单里应有「预览」")
        preview.tap()
        XCTAssertTrue(app.buttons["Done"].waitForExistence(timeout: 3), "应弹出快速预览")
        app.buttons["Done"].tap()
        XCTAssertTrue(app.buttons["Done"].waitForNonExistence(timeout: 3))
    }

    func testOpenDetailsFromMenu() {
        longPressCard()
        let open = app.buttons["Open Details"]
        XCTAssertTrue(open.waitForExistence(timeout: 3), "长按菜单里应有「打开详情」")
        open.tap()
        XCTAssertTrue(app.buttons["More"].waitForExistence(timeout: 3), "应进入详情页")
    }
}
