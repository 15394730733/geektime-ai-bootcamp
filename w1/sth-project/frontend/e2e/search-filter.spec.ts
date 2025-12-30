import { test, expect } from '@playwright/test'

/**
 * 搜索和筛选功能端到端测试
 * 测试 Ticket 的搜索、筛选和分页功能
 */

test.describe('搜索和筛选功能', () => {
  test.beforeEach(async ({ page }) => {
    // 导航到 Ticket 管理页面
    await page.goto('/tickets')
    await page.waitForLoadState('networkidle')
  })

  /**
   * 测试按标题搜索 Ticket
   */
  test('按标题搜索 Ticket', async ({ page }) => {
    // 创建多个 Ticket
    const ticketTitles = ['紧急任务', '重要会议', '普通事项', '低优先级任务']
    for (const title of ticketTitles) {
      await page.click('button:has-text("新建 Ticket")')
      await page.fill('input[placeholder="请输入 Ticket 标题"]', title)
      await page.fill('textarea[placeholder="请输入 Ticket 描述"]', '测试描述')
      await page.click('button:has-text("确定")')
      await expect(page.locator('.el-message--success')).toBeVisible()
    }

    // 搜索包含"任务"的 Ticket
    await page.fill('input[placeholder="搜索 Ticket 标题"]', '任务')

    // 等待搜索结果加载
    await page.waitForTimeout(500)

    // 验证只显示匹配的 Ticket
    await expect(page.locator('text=紧急任务')).toBeVisible()
    await expect(page.locator('text=低优先级任务')).toBeVisible()
    await expect(page.locator('text=重要会议')).not.toBeVisible()
    await expect(page.locator('text=普通事项')).not.toBeVisible()

    // 清空搜索
    await page.click('.el-input__clear')

    // 验证所有 Ticket 都显示
    await expect(page.locator('text=紧急任务')).toBeVisible()
    await expect(page.locator('text=重要会议')).toBeVisible()
    await expect(page.locator('text=普通事项')).toBeVisible()
    await expect(page.locator('text=低优先级任务')).toBeVisible()
  })

  /**
   * 测试搜索不区分大小写
   */
  test('搜索不区分大小写', async ({ page }) => {
    // 创建一个 Ticket
    await page.click('button:has-text("新建 Ticket")')
    await page.fill('input[placeholder="请输入 Ticket 标题"]', 'Test Ticket')
    await page.fill('textarea[placeholder="请输入 Ticket 描述"]', '测试描述')
    await page.click('button:has-text("确定")')
    await expect(page.locator('.el-message--success')).toBeVisible()

    // 使用小写搜索
    await page.fill('input[placeholder="搜索 Ticket 标题"]', 'test')
    await page.waitForTimeout(500)

    // 验证找到 Ticket
    await expect(page.locator('text=Test Ticket')).toBeVisible()

    // 使用大写搜索
    await page.fill('input[placeholder="搜索 Ticket 标题"]', 'TEST')
    await page.waitForTimeout(500)

    // 验证找到 Ticket
    await expect(page.locator('text=Test Ticket')).toBeVisible()
  })

  /**
   * 测试搜索支持部分匹配
   */
  test('搜索支持部分匹配', async ({ page }) => {
    // 创建多个 Ticket
    const ticketTitles = ['前端开发任务', '后端开发任务', '测试任务', '部署任务']
    for (const title of ticketTitles) {
      await page.click('button:has-text("新建 Ticket")')
      await page.fill('input[placeholder="请输入 Ticket 标题"]', title)
      await page.fill('textarea[placeholder="请输入 Ticket 描述"]', '测试描述')
      await page.click('button:has-text("确定")')
      await expect(page.locator('.el-message--success')).toBeVisible()
    }

    // 搜索"开发"
    await page.fill('input[placeholder="搜索 Ticket 标题"]', '开发')
    await page.waitForTimeout(500)

    // 验证显示包含"开发"的 Ticket
    await expect(page.locator('text=前端开发任务')).toBeVisible()
    await expect(page.locator('text=后端开发任务')).toBeVisible()
    await expect(page.locator('text=测试任务')).not.toBeVisible()
    await expect(page.locator('text=部署任务')).not.toBeVisible()
  })

  /**
   * 测试筛选状态 - 进行中
   */
  test('筛选状态 - 进行中', async ({ page }) => {
    // 创建多个 Ticket，部分完成
    const ticketTitles = ['任务1', '任务2', '任务3']
    for (const title of ticketTitles) {
      await page.click('button:has-text("新建 Ticket")')
      await page.fill('input[placeholder="请输入 Ticket 标题"]', title)
      await page.fill('textarea[placeholder="请输入 Ticket 描述"]', '测试描述')
      await page.click('button:has-text("确定")')
      await expect(page.locator('.el-message--success')).toBeVisible()
    }

    // 标记第一个 Ticket 为完成
    const firstTicket = page.locator('.ticket-item').first()
    await firstTicket.locator('button:has-text("完成")').click()

    // 筛选进行中的 Ticket
    await page.click('.el-select:has-text("筛选状态")')
    await page.click('.el-select-dropdown__item:has-text("进行中")')

    // 验证只显示未完成的 Ticket
    await expect(page.locator('text=任务2')).toBeVisible()
    await expect(page.locator('text=任务3')).toBeVisible()
    await expect(page.locator('text=任务1')).not.toBeVisible()
  })

  /**
   * 测试筛选状态 - 已完成
   */
  test('筛选状态 - 已完成', async ({ page }) => {
    // 创建多个 Ticket
    const ticketTitles = ['任务1', '任务2', '任务3']
    for (const title of ticketTitles) {
      await page.click('button:has-text("新建 Ticket")')
      await page.fill('input[placeholder="请输入 Ticket 标题"]', title)
      await page.fill('textarea[placeholder="请输入 Ticket 描述"]', '测试描述')
      await page.click('button:has-text("确定")')
      await expect(page.locator('.el-message--success')).toBeVisible()
    }

    // 标记第一个 Ticket 为完成
    const firstTicket = page.locator('.ticket-item').first()
    await firstTicket.locator('button:has-text("完成")').click()

    // 筛选已完成的 Ticket
    await page.click('.el-select:has-text("筛选状态")')
    await page.click('.el-select-dropdown__item:has-text("已完成")')

    // 验证只显示已完成的 Ticket
    await expect(page.locator('text=任务1')).toBeVisible()
    await expect(page.locator('text=任务2')).not.toBeVisible()
    await expect(page.locator('text=任务3')).not.toBeVisible()
  })

  /**
   * 测试筛选标签
   */
  test('筛选标签', async ({ page }) => {
    // 先创建标签
    await page.goto('/tags')
    await page.waitForLoadState('networkidle')

    const tagNames = ['紧急', '重要']
    for (const name of tagNames) {
      await page.click('button:has-text("新建标签")')
      await page.fill('input[placeholder="请输入标签名称"]', name)
      await page.click('button:has-text("确定")')
      await expect(page.locator('.el-message--success')).toBeVisible()
    }

    // 返回 Ticket 页面
    await page.goto('/tickets')
    await page.waitForLoadState('networkidle')

    // 创建带标签的 Ticket
    await page.click('button:has-text("新建 Ticket")')
    await page.fill('input[placeholder="请输入 Ticket 标题"]', '紧急任务')
    await page.fill('textarea[placeholder="请输入 Ticket 描述"]', '测试描述')
    
    // 选择标签（假设有标签选择器）
    const tagSelector = page.locator('.el-select:has-text("选择标签")')
    if (await tagSelector.isVisible()) {
      await tagSelector.click()
      await page.click('.el-select-dropdown__item:has-text("紧急")')
    }
    
    await page.click('button:has-text("确定")')
    await expect(page.locator('.el-message--success')).toBeVisible()

    // 筛选标签
    await page.click('.el-select:has-text("筛选标签")')
    await page.click('.el-select-dropdown__item:has-text("紧急")')

    // 验证只显示带该标签的 Ticket
    await expect(page.locator('text=紧急任务')).toBeVisible()
  })

  /**
   * 测试组合搜索 - 关键词 + 状态
   */
  test('组合搜索 - 关键词 + 状态', async ({ page }) => {
    // 创建多个 Ticket
    const ticketTitles = ['紧急任务1', '紧急任务2', '普通任务']
    for (const title of ticketTitles) {
      await page.click('button:has-text("新建 Ticket")')
      await page.fill('input[placeholder="请输入 Ticket 标题"]', title)
      await page.fill('textarea[placeholder="请输入 Ticket 描述"]', '测试描述')
      await page.click('button:has-text("确定")')
      await expect(page.locator('.el-message--success')).toBeVisible()
    }

    // 标记第一个 Ticket 为完成
    const firstTicket = page.locator('.ticket-item').first()
    await firstTicket.locator('button:has-text("完成")').click()

    // 搜索"紧急"并筛选"进行中"
    await page.fill('input[placeholder="搜索 Ticket 标题"]', '紧急')
    await page.click('.el-select:has-text("筛选状态")')
    await page.click('.el-select-dropdown__item:has-text("进行中")')

    // 验证只显示进行中的"紧急"任务
    await expect(page.locator('text=紧急任务2')).toBeVisible()
    await expect(page.locator('text=紧急任务1')).not.toBeVisible()
    await expect(page.locator('text=普通任务')).not.toBeVisible()
  })

  /**
   * 测试清空所有筛选条件
   */
  test('清空所有筛选条件', async ({ page }) => {
    // 创建多个 Ticket
    const ticketTitles = ['任务1', '任务2']
    for (const title of ticketTitles) {
      await page.click('button:has-text("新建 Ticket")')
      await page.fill('input[placeholder="请输入 Ticket 标题"]', title)
      await page.fill('textarea[placeholder="请输入 Ticket 描述"]', '测试描述')
      await page.click('button:has-text("确定")')
      await expect(page.locator('.el-message--success')).toBeVisible()
    }

    // 应用筛选条件
    await page.fill('input[placeholder="搜索 Ticket 标题"]', '任务1')
    await page.click('.el-select:has-text("筛选状态")')
    await page.click('.el-select-dropdown__item:has-text("进行中")')

    // 清空搜索
    await page.click('.el-input__clear')

    // 清空状态筛选
    await page.click('.el-select:has-text("进行中") .el-select__caret')

    // 验证所有 Ticket 都显示
    await expect(page.locator('text=任务1')).toBeVisible()
    await expect(page.locator('text=任务2')).toBeVisible()
  })

  /**
   * 测试分页功能
   */
  test('分页功能', async ({ page }) => {
    // 创建超过一页的 Ticket（假设每页显示 20 条）
    for (let i = 1; i <= 25; i++) {
      await page.click('button:has-text("新建 Ticket")')
      await page.fill('input[placeholder="请输入 Ticket 标题"]', `任务${i}`)
      await page.fill('textarea[placeholder="请输入 Ticket 描述"]', '测试描述')
      await page.click('button:has-text("确定")')
      await expect(page.locator('.el-message--success')).toBeVisible()
    }

    // 验证第一页显示 20 条
    const firstPageTickets = await page.locator('.ticket-item').count()
    expect(firstPageTickets).toBeLessThanOrEqual(20)

    // 点击下一页
    await page.click('.el-pagination button:has-text(">")')

    // 验证第二页显示剩余的 Ticket
    const secondPageTickets = await page.locator('.ticket-item').count()
    expect(secondPageTickets).toBe(5)

    // 点击上一页
    await page.click('.el-pagination button:has-text("<")')

    // 验证回到第一页
    const backToFirstPageTickets = await page.locator('.ticket-item').count()
    expect(backToFirstPageTickets).toBeLessThanOrEqual(20)
  })

  /**
   * 测试每页显示数量切换
   */
  test('每页显示数量切换', async ({ page }) => {
    // 创建多个 Ticket
    for (let i = 1; i <= 25; i++) {
      await page.click('button:has-text("新建 Ticket")')
      await page.fill('input[placeholder="请输入 Ticket 标题"]', `任务${i}`)
      await page.fill('textarea[placeholder="请输入 Ticket 描述"]', '测试描述')
      await page.click('button:has-text("确定")')
      await expect(page.locator('.el-message--success')).toBeVisible()
    }

    // 切换到每页 10 条
    await page.click('.el-pagination__sizes .el-select')
    await page.click('.el-select-dropdown__item:has-text("10 条/页")')

    // 验证显示 10 条
    const tickets10 = await page.locator('.ticket-item').count()
    expect(tickets10).toBe(10)

    // 切换到每页 50 条
    await page.click('.el-pagination__sizes .el-select')
    await page.click('.el-select-dropdown__item:has-text("50 条/页")')

    // 验证显示所有 25 条
    const tickets50 = await page.locator('.ticket-item').count()
    expect(tickets50).toBe(25)
  })

  /**
   * 测试跳转到指定页
   */
  test('跳转到指定页', async ({ page }) => {
    // 创建超过两页的 Ticket
    for (let i = 1; i <= 25; i++) {
      await page.click('button:has-text("新建 Ticket")')
      await page.fill('input[placeholder="请输入 Ticket 标题"]', `任务${i}`)
      await page.fill('textarea[placeholder="请输入 Ticket 描述"]', '测试描述')
      await page.click('button:has-text("确定")')
      await expect(page.locator('.el-message--success')).toBeVisible()
    }

    // 输入页码并跳转
    await page.fill('.el-pagination__jump input', '2')
    await page.press('.el-pagination__jump input', 'Enter')

    // 验证跳转到第二页
    await expect(page.locator('.el-pager .number.is-active')).toHaveText('2')
  })

  /**
   * 测试搜索结果为空时的显示
   */
  test('搜索结果为空时的显示', async ({ page }) => {
    // 搜索不存在的 Ticket
    await page.fill('input[placeholder="搜索 Ticket 标题"]', '不存在的 Ticket')

    // 验证空状态显示
    await expect(page.locator('.el-empty')).toBeVisible()
    await expect(page.locator('text=暂无 Ticket')).toBeVisible()
  })

  /**
   * 测试搜索防抖
   */
  test('搜索防抖', async ({ page }) => {
    // 创建一个 Ticket
    await page.click('button:has-text("新建 Ticket")')
    await page.fill('input[placeholder="请输入 Ticket 标题"]', '测试 Ticket')
    await page.fill('textarea[placeholder="请输入 Ticket 描述"]', '测试描述')
    await page.click('button:has-text("确定")')
    await expect(page.locator('.el-message--success')).toBeVisible()

    // 快速输入多个字符
    await page.fill('input[placeholder="搜索 Ticket 标题"]', '测')
    await page.fill('input[placeholder="搜索 Ticket 标题"]', '测试')
    await page.fill('input[placeholder="搜索 Ticket 标题"]', '测试 T')
    await page.fill('input[placeholder="搜索 Ticket 标题"]', '测试 Ti')
    await page.fill('input[placeholder="搜索 Ticket 标题"]', '测试 Tic')
    await page.fill('input[placeholder="搜索 Ticket 标题"]', '测试 Tick')
    await page.fill('input[placeholder="搜索 Ticket 标题"]', '测试 Ticke')
    await page.fill('input[placeholder="搜索 Ticket 标题"]', '测试 Ticket')

    // 等待防抖时间后验证结果
    await page.waitForTimeout(500)
    await expect(page.locator('text=测试 Ticket')).toBeVisible()
  })

  /**
   * 测试标签筛选的可搜索功能
   */
  test('标签筛选的可搜索功能', async ({ page }) => {
    // 先创建多个标签
    await page.goto('/tags')
    await page.waitForLoadState('networkidle')

    const tagNames = ['紧急', '重要', '普通', '低优先级', '高优先级']
    for (const name of tagNames) {
      await page.click('button:has-text("新建标签")')
      await page.fill('input[placeholder="请输入标签名称"]', name)
      await page.click('button:has-text("确定")')
      await expect(page.locator('.el-message--success')).toBeVisible()
    }

    // 返回 Ticket 页面
    await page.goto('/tickets')
    await page.waitForLoadState('networkidle')

    // 点击标签筛选下拉框
    await page.click('.el-select:has-text("筛选标签")')

    // 在下拉框中搜索标签
    await page.fill('.el-select-dropdown .el-input__inner', '优先级')

    // 验证只显示匹配的标签选项
    await expect(page.locator('.el-select-dropdown__item:has-text("低优先级")')).toBeVisible()
    await expect(page.locator('.el-select-dropdown__item:has-text("高优先级")')).toBeVisible()
    await expect(page.locator('.el-select-dropdown__item:has-text("紧急")')).not.toBeVisible()
  })

  /**
   * 测试搜索时保留其他筛选条件
   */
  test('搜索时保留其他筛选条件', async ({ page }) => {
    // 创建多个 Ticket
    const ticketTitles = ['紧急任务1', '紧急任务2', '普通任务']
    for (const title of ticketTitles) {
      await page.click('button:has-text("新建 Ticket")')
      await page.fill('input[placeholder="请输入 Ticket 标题"]', title)
      await page.fill('textarea[placeholder="请输入 Ticket 描述"]', '测试描述')
      await page.click('button:has-text("确定")')
      await expect(page.locator('.el-message--success')).toBeVisible()
    }

    // 先筛选状态
    await page.click('.el-select:has-text("筛选状态")')
    await page.click('.el-select-dropdown__item:has-text("进行中")')

    // 然后搜索
    await page.fill('input[placeholder="搜索 Ticket 标题"]', '紧急')

    // 验证同时应用了两个筛选条件
    await expect(page.locator('text=紧急任务1')).toBeVisible()
    await expect(page.locator('text=紧急任务2')).toBeVisible()
    await expect(page.locator('text=普通任务')).not.toBeVisible()
  })

  /**
   * 测试搜索结果总数显示
   */
  test('搜索结果总数显示', async ({ page }) => {
    // 创建多个 Ticket
    for (let i = 1; i <= 5; i++) {
      await page.click('button:has-text("新建 Ticket")')
      await page.fill('input[placeholder="请输入 Ticket 标题"]', `任务${i}`)
      await page.fill('textarea[placeholder="请输入 Ticket 描述"]', '测试描述')
      await page.click('button:has-text("确定")')
      await expect(page.locator('.el-message--success')).toBeVisible()
    }

    // 验证总数显示
    await expect(page.locator('.el-pagination__total')).toContainText('共 5 条')

    // 搜索
    await page.fill('input[placeholder="搜索 Ticket 标题"]', '任务')

    // 验证搜索结果总数
    await expect(page.locator('.el-pagination__total')).toContainText('共 5 条')

    // 搜索不存在的 Ticket
    await page.fill('input[placeholder="搜索 Ticket 标题"]', '不存在的')

    // 验证搜索结果为 0
    await expect(page.locator('.el-pagination__total')).toContainText('共 0 条')
  })
})
