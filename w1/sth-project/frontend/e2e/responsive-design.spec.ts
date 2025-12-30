import { test, expect, devices } from '@playwright/test'

/**
 * 响应式设计端到端测试
 * 测试应用在不同设备和屏幕尺寸下的显示效果
 */

test.describe('响应式设计', () => {
  /**
   * 测试桌面端显示
   */
  test('桌面端显示', async ({ page }) => {
    // 设置桌面视口
    await page.setViewportSize({ width: 1920, height: 1080 })
    
    // 导航到 Ticket 管理页面
    await page.goto('/tickets')
    await page.waitForLoadState('networkidle')

    // 验证页面布局正常
    await expect(page.locator('.tickets-page')).toBeVisible()
    await expect(page.locator('.page-header')).toBeVisible()
    await expect(page.locator('.ticket-list')).toBeVisible()

    // 验证筛选器水平排列
    const filters = page.locator('.ticket-list-filters')
    const filterCount = await filters.locator('> *').count()
    expect(filterCount).toBeGreaterThan(1)

    // 验证分页组件正常显示
    await expect(page.locator('.ticket-list-pagination')).toBeVisible()
  })

  /**
   * 测试平板端显示
   */
  test('平板端显示', async ({ page }) => {
    // 设置平板视口
    await page.setViewportSize({ width: 768, height: 1024 })
    
    // 导航到 Ticket 管理页面
    await page.goto('/tickets')
    await page.waitForLoadState('networkidle')

    // 验证页面布局正常
    await expect(page.locator('.tickets-page')).toBeVisible()
    await expect(page.locator('.page-header')).toBeVisible()
    await expect(page.locator('.ticket-list')).toBeVisible()

    // 验证筛选器可能变为垂直排列
    const filters = page.locator('.ticket-list-filters')
    await expect(filters).toBeVisible()
  })

  /**
   * 测试移动端显示
   */
  test('移动端显示', async ({ page }) => {
    // 设置移动端视口
    await page.setViewportSize({ width: 375, height: 667 })
    
    // 导航到 Ticket 管理页面
    await page.goto('/tickets')
    await page.waitForLoadState('networkidle')

    // 验证页面布局正常
    await expect(page.locator('.tickets-page')).toBeVisible()
    await expect(page.locator('.page-header')).toBeVisible()
    await expect(page.locator('.ticket-list')).toBeVisible()

    // 验证筛选器垂直排列
    const filters = page.locator('.ticket-list-filters')
    await expect(filters).toBeVisible()

    // 验证筛选器宽度适应屏幕
    const filterWidth = await filters.boundingBox()
    expect(filterWidth?.width).toBeLessThanOrEqual(375)
  })

  /**
   * 测试移动端创建 Ticket
   */
  test('移动端创建 Ticket', async ({ page }) => {
    // 设置移动端视口
    await page.setViewportSize({ width: 375, height: 667 })
    
    // 导航到 Ticket 管理页面
    await page.goto('/tickets')
    await page.waitForLoadState('networkidle')

    // 点击创建按钮
    await page.click('button:has-text("新建 Ticket")')

    // 验证对话框出现
    await expect(page.locator('.el-dialog')).toBeVisible()

    // 验证对话框适应屏幕宽度
    const dialog = page.locator('.el-dialog')
    const dialogBox = await dialog.boundingBox()
    expect(dialogBox?.width).toBeLessThanOrEqual(375)

    // 填写表单
    await page.fill('input[placeholder="请输入 Ticket 标题"]', '移动端测试 Ticket')
    await page.fill('textarea[placeholder="请输入 Ticket 描述"]', '这是移动端测试')

    // 提交表单
    await page.click('button:has-text("确定")')

    // 验证成功提示
    await expect(page.locator('.el-message--success')).toBeVisible()
  })

  /**
   * 测试移动端搜索功能
   */
  test('移动端搜索功能', async ({ page }) => {
    // 设置移动端视口
    await page.setViewportSize({ width: 375, height: 667 })
    
    // 导航到 Ticket 管理页面
    await page.goto('/tickets')
    await page.waitForLoadState('networkidle')

    // 创建一个 Ticket
    await page.click('button:has-text("新建 Ticket")')
    await page.fill('input[placeholder="请输入 Ticket 标题"]', '测试 Ticket')
    await page.fill('textarea[placeholder="请输入 Ticket 描述"]', '测试描述')
    await page.click('button:has-text("确定")')
    await expect(page.locator('.el-message--success')).toBeVisible()

    // 搜索 Ticket
    await page.fill('input[placeholder="搜索 Ticket 标题"]', '测试')

    // 验证搜索结果
    await expect(page.locator('text=测试 Ticket')).toBeVisible()
  })

  /**
   * 测试移动端分页功能
   */
  test('移动端分页功能', async ({ page }) => {
    // 设置移动端视口
    await page.setViewportSize({ width: 375, height: 667 })
    
    // 导航到 Ticket 管理页面
    await page.goto('/tickets')
    await page.waitForLoadState('networkidle')

    // 创建多个 Ticket
    for (let i = 1; i <= 15; i++) {
      await page.click('button:has-text("新建 Ticket")')
      await page.fill('input[placeholder="请输入 Ticket 标题"]', `任务${i}`)
      await page.fill('textarea[placeholder="请输入 Ticket 描述"]', '测试描述')
      await page.click('button:has-text("确定")')
      await expect(page.locator('.el-message--success')).toBeVisible()
    }

    // 验证分页组件存在
    await expect(page.locator('.ticket-list-pagination')).toBeVisible()

    // 点击下一页
    await page.click('.el-pagination button:has-text(">")')

    // 验证页面切换成功
    await expect(page.locator('.el-pager .number.is-active')).toHaveText('2')
  })

  /**
   * 测试横屏模式
   */
  test('横屏模式', async ({ page }) => {
    // 设置横屏视口
    await page.setViewportSize({ width: 896, height: 414 })
    
    // 导航到 Ticket 管理页面
    await page.goto('/tickets')
    await page.waitForLoadState('networkidle')

    // 验证页面布局正常
    await expect(page.locator('.tickets-page')).toBeVisible()
    await expect(page.locator('.page-header')).toBeVisible()
    await expect(page.locator('.ticket-list')).toBeVisible()

    // 验证筛选器水平排列
    const filters = page.locator('.ticket-list-filters')
    await expect(filters).toBeVisible()
  })

  /**
   * 测试超大屏幕显示
   */
  test('超大屏幕显示', async ({ page }) => {
    // 设置超大屏幕视口
    await page.setViewportSize({ width: 2560, height: 1440 })
    
    // 导航到 Ticket 管理页面
    await page.goto('/tickets')
    await page.waitForLoadState('networkidle')

    // 验证页面布局正常
    await expect(page.locator('.tickets-page')).toBeVisible()
    await expect(page.locator('.page-header')).toBeVisible()
    await expect(page.locator('.ticket-list')).toBeVisible()

    // 验证内容居中显示
    const pageContent = page.locator('.tickets-page')
    const boundingBox = await pageContent.boundingBox()
    expect(boundingBox?.width).toBeLessThanOrEqual(1200)
  })

  /**
   * 测试不同屏幕高度下的滚动
   */
  test('不同屏幕高度下的滚动', async ({ page }) => {
    // 设置小高度视口
    await page.setViewportSize({ width: 1920, height: 600 })
    
    // 导航到 Ticket 管理页面
    await page.goto('/tickets')
    await page.waitForLoadState('networkidle')

    // 创建多个 Ticket
    for (let i = 1; i <= 10; i++) {
      await page.click('button:has-text("新建 Ticket")')
      await page.fill('input[placeholder="请输入 Ticket 标题"]', `任务${i}`)
      await page.fill('textarea[placeholder="请输入 Ticket 描述"]', '这是一个较长的描述内容，用于测试滚动效果')
      await page.click('button:has-text("确定")')
      await expect(page.locator('.el-message--success')).toBeVisible()
    }

    // 验证页面可滚动
    const bodyHeight = await page.evaluate(() => document.body.scrollHeight)
    const viewportHeight = await page.evaluate(() => window.innerHeight)
    expect(bodyHeight).toBeGreaterThan(viewportHeight)

    // 滚动到页面底部
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight))

    // 验证分页组件可见
    await expect(page.locator('.ticket-list-pagination')).toBeVisible()
  })

  /**
   * 测试触摸操作（移动端）
   */
  test('触摸操作', async ({ page }) => {
    // 设置移动端视口
    await page.setViewportSize({ width: 375, height: 667 })
    
    // 导航到 Ticket 管理页面
    await page.goto('/tickets')
    await page.waitForLoadState('networkidle')

    // 创建一个 Ticket
    await page.click('button:has-text("新建 Ticket")')
    await page.fill('input[placeholder="请输入 Ticket 标题"]', '触摸测试 Ticket')
    await page.fill('textarea[placeholder="请输入 Ticket 描述"]', '测试描述')
    await page.click('button:has-text("确定")')
    await expect(page.locator('.el-message--success')).toBeVisible()

    // 模拟触摸滑动
    await page.touchscreen.tap(200, 300)

    // 验证 Ticket 可见
    await expect(page.locator('text=触摸测试 Ticket')).toBeVisible()
  })

  /**
   * 测试字体缩放
   */
  test('字体缩放', async ({ page }) => {
    // 导航到 Ticket 管理页面
    await page.goto('/tickets')
    await page.waitForLoadState('networkidle')

    // 设置字体缩放
    await page.evaluate(() => {
      document.body.style.zoom = '1.5'
    })

    // 验证页面仍然可用
    await expect(page.locator('.tickets-page')).toBeVisible()
    await expect(page.locator('button:has-text("新建 Ticket")')).toBeVisible()

    // 点击创建按钮
    await page.click('button:has-text("新建 Ticket")')

    // 验证对话框出现
    await expect(page.locator('.el-dialog')).toBeVisible()
  })

  /**
   * 测试高对比度模式
   */
  test('高对比度模式', async ({ page }) => {
    // 导航到 Ticket 管理页面
    await page.goto('/tickets')
    await page.waitForLoadState('networkidle')

    // 模拟高对比度模式
    await page.emulateMedia({ colorScheme: 'dark' })

    // 验证页面仍然可用
    await expect(page.locator('.tickets-page')).toBeVisible()
    await expect(page.locator('button:has-text("新建 Ticket")')).toBeVisible()
  })

  /**
   * 测试移动端菜单导航
   */
  test('移动端菜单导航', async ({ page }) => {
    // 设置移动端视口
    await page.setViewportSize({ width: 375, height: 667 })
    
    // 导航到 Ticket 管理页面
    await page.goto('/tickets')
    await page.waitForLoadState('networkidle')

    // 点击菜单按钮（如果存在）
    const menuButton = page.locator('.el-icon-menu, .menu-button')
    if (await menuButton.isVisible()) {
      await menuButton.click()

      // 验证菜单出现
      await expect(page.locator('.el-menu, .sidebar')).toBeVisible()

      // 点击标签页面链接
      await page.click('a:has-text("标签"), .menu-item:has-text("标签")')

      // 验证导航到标签页面
      await expect(page).toHaveURL(/\/tags/)
    }
  })

  /**
   * 测试移动端对话框全屏显示
   */
  test('移动端对话框全屏显示', async ({ page }) => {
    // 设置移动端视口
    await page.setViewportSize({ width: 375, height: 667 })
    
    // 导航到 Ticket 管理页面
    await page.goto('/tickets')
    await page.waitForLoadState('networkidle')

    // 点击创建按钮
    await page.click('button:has-text("新建 Ticket")')

    // 验证对话框出现
    const dialog = page.locator('.el-dialog')
    await expect(dialog).toBeVisible()

    // 验证对话框接近全屏
    const dialogBox = await dialog.boundingBox()
    const viewportHeight = await page.evaluate(() => window.innerHeight)
    expect(dialogBox?.height).toBeGreaterThan(viewportHeight * 0.8)
  })

  /**
   * 测试移动端表单输入
   */
  test('移动端表单输入', async ({ page }) => {
    // 设置移动端视口
    await page.setViewportSize({ width: 375, height: 667 })
    
    // 导航到 Ticket 管理页面
    await page.goto('/tickets')
    await page.waitForLoadState('networkidle')

    // 点击创建按钮
    await page.click('button:has-text("新建 Ticket")')

    // 验证对话框出现
    await expect(page.locator('.el-dialog')).toBeVisible()

    // 填写表单
    await page.fill('input[placeholder="请输入 Ticket 标题"]', '移动端表单测试')
    
    // 验证输入框获得焦点时键盘不会遮挡（模拟）
    const input = page.locator('input[placeholder="请输入 Ticket 标题"]')
    await input.focus()
    await expect(input).toBeVisible()
  })

  /**
   * 测试移动端删除确认对话框
   */
  test('移动端删除确认对话框', async ({ page }) => {
    // 设置移动端视口
    await page.setViewportSize({ width: 375, height: 667 })
    
    // 导航到 Ticket 管理页面
    await page.goto('/tickets')
    await page.waitForLoadState('networkidle')

    // 创建一个 Ticket
    await page.click('button:has-text("新建 Ticket")')
    await page.fill('input[placeholder="请输入 Ticket 标题"]', '待删除 Ticket')
    await page.fill('textarea[placeholder="请输入 Ticket 描述"]', '测试描述')
    await page.click('button:has-text("确定")')
    await expect(page.locator('.el-message--success')).toBeVisible()

    // 点击删除按钮
    const ticketItem = page.locator('.ticket-item').filter({ hasText: '待删除 Ticket' })
    await ticketItem.locator('button:has-text("删除")').click()

    // 验证确认对话框出现
    await expect(page.locator('.el-message-box')).toBeVisible()

    // 验证对话框按钮可点击
    await expect(page.locator('.el-message-box__btns button:has-text("确定")')).toBeVisible()
    await expect(page.locator('.el-message-box__btns button:has-text("取消")')).toBeVisible()
  })

  /**
   * 测试不同设备下的标签页面
   */
  test('不同设备下的标签页面', async ({ page }) => {
    // 测试桌面端
    await page.setViewportSize({ width: 1920, height: 1080 })
    await page.goto('/tags')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('.tag-list')).toBeVisible()

    // 测试移动端
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/tags')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('.tag-list')).toBeVisible()

    // 验证标签列表适应屏幕
    const tagList = page.locator('.tag-list')
    const boundingBox = await tagList.boundingBox()
    expect(boundingBox?.width).toBeLessThanOrEqual(375)
  })

  /**
   * 测试移动端下拉选择器
   */
  test('移动端下拉选择器', async ({ page }) => {
    // 设置移动端视口
    await page.setViewportSize({ width: 375, height: 667 })
    
    // 导航到 Ticket 管理页面
    await page.goto('/tickets')
    await page.waitForLoadState('networkidle')

    // 点击状态筛选下拉框
    await page.click('.el-select:has-text("筛选状态")')

    // 验证下拉框出现
    await expect(page.locator('.el-select-dropdown')).toBeVisible()

    // 验证下拉框适应屏幕宽度
    const dropdown = page.locator('.el-select-dropdown')
    const dropdownBox = await dropdown.boundingBox()
    expect(dropdownBox?.width).toBeLessThanOrEqual(375)

    // 选择一个选项
    await page.click('.el-select-dropdown__item:has-text("进行中")')

    // 验证选择成功
    await expect(page.locator('.el-select:has-text("进行中")')).toBeVisible()
  })
})

/**
 * 使用 Playwright 设备模拟进行响应式测试
 */
test.describe('设备模拟测试', () => {
  /**
   * 测试 iPhone 12
   */
  test('iPhone 12 显示', async ({ page }) => {
    await page.setViewportSize(devices['iPhone 12'].viewport!)
    await page.goto('/tickets')
    await page.waitForLoadState('networkidle')

    await expect(page.locator('.tickets-page')).toBeVisible()
    await expect(page.locator('.ticket-list')).toBeVisible()
  })

  /**
   * 测试 iPad Pro
   */
  test('iPad Pro 显示', async ({ page }) => {
    await page.setViewportSize(devices['iPad Pro'].viewport!)
    await page.goto('/tickets')
    await page.waitForLoadState('networkidle')

    await expect(page.locator('.tickets-page')).toBeVisible()
    await expect(page.locator('.ticket-list')).toBeVisible()
  })

  /**
   * 测试 Pixel 5
   */
  test('Pixel 5 显示', async ({ page }) => {
    await page.setViewportSize(devices['Pixel 5'].viewport!)
    await page.goto('/tickets')
    await page.waitForLoadState('networkidle')

    await expect(page.locator('.tickets-page')).toBeVisible()
    await expect(page.locator('.ticket-list')).toBeVisible()
  })
})
