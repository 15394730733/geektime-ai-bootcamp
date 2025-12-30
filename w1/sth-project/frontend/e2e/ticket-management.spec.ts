import { test, expect } from '@playwright/test'

test.describe('Ticket 管理端到端测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('创建新 Ticket', async ({ page }) => {
    // 点击创建按钮
    await page.click('button:has-text("新建 Ticket")')
    
    // 填写表单
    await page.fill('input[placeholder="请输入 Ticket 标题"]', '测试 Ticket')
    await page.fill('textarea[placeholder="请输入 Ticket 描述"]', '这是测试描述')
    
    // 提交表单
    await page.click('button:has-text("确定")')
    
    // 验证成功提示
    await expect(page.locator('.el-message--success')).toBeVisible()
    
    // 验证 Ticket 列表中包含新创建的 Ticket
    await expect(page.locator('text=测试 Ticket')).toBeVisible()
  })

  test('创建 Ticket 时标题为空应显示验证错误', async ({ page }) => {
    // 点击创建按钮
    await page.click('button:has-text("新建 Ticket")')
    
    // 不填写标题直接提交
    await page.click('button:has-text("确定")')
    
    // 验证显示验证错误
    await expect(page.locator('.el-form-item__error')).toBeVisible()
    await expect(page.locator('.el-form-item__error')).toContainText('请输入 Ticket 标题')
  })

  test('编辑 Ticket', async ({ page }) => {
    // 假设列表中有一个 Ticket
    const ticketItem = page.locator('.ticket-item').first()
    
    // 点击编辑按钮
    await ticketItem.locator('button:has-text("编辑")').click()
    
    // 修改标题
    await page.fill('input[placeholder="请输入 Ticket 标题"]', '修改后的标题')
    
    // 提交表单
    await page.click('button:has-text("确定")')
    
    // 验证成功提示
    await expect(page.locator('.el-message--success')).toBeVisible()
    
    // 验证标题已更新
    await expect(page.locator('text=修改后的标题')).toBeVisible()
  })

  test('删除 Ticket', async ({ page }) => {
    // 假设列表中有一个 Ticket
    const ticketItem = page.locator('.ticket-item').first()
    
    // 点击删除按钮
    await ticketItem.locator('button:has-text("删除")').click()
    
    // 确认删除
    await page.click('.el-button--primary:has-text("确定")')
    
    // 验证成功提示
    await expect(page.locator('.el-message--success')).toBeVisible()
    
    // 验证 Ticket 已从列表中删除
    await expect(ticketItem).not.toBeVisible()
  })

  test('切换 Ticket 状态', async ({ page }) => {
    // 假设列表中有一个未完成的 Ticket
    const ticketItem = page.locator('.ticket-item').first()
    
    // 点击状态切换按钮
    await ticketItem.locator('.el-switch').click()
    
    // 验证状态已切换
    await expect(ticketItem.locator('.el-switch.is-checked')).toBeVisible()
  })

  test('分页查看 Ticket 列表', async ({ page }) => {
    // 等待列表加载
    await page.waitForSelector('.ticket-item')
    
    // 检查分页组件是否存在
    await expect(page.locator('.el-pagination')).toBeVisible()
    
    // 点击下一页
    await page.click('.el-pager .number:has-text("2")')
    
    // 验证页面已切换
    await expect(page.locator('.el-pager .number.is-active')).toContainText('2')
  })

  test('搜索 Ticket', async ({ page }) => {
    // 输入搜索关键词
    await page.fill('input[placeholder="搜索 Ticket..."]', '测试')
    
    // 点击搜索按钮
    await page.click('button:has-text("搜索")')
    
    // 等待搜索结果
    await page.waitForSelector('.ticket-item')
    
    // 验证搜索结果
    const ticketItems = page.locator('.ticket-item')
    const count = await ticketItems.count()
    expect(count).toBeGreaterThan(0)
  })

  test('清空搜索', async ({ page }) => {
    // 先进行搜索
    await page.fill('input[placeholder="搜索 Ticket..."]', '测试')
    await page.click('button:has-text("搜索")')
    await page.waitForSelector('.ticket-item')
    
    // 清空搜索
    await page.fill('input[placeholder="搜索 Ticket..."]', '')
    await page.click('button:has-text("搜索")')
    
    // 验证显示所有 Ticket
    await page.waitForSelector('.ticket-item')
  })

  test('创建带标签的 Ticket', async ({ page }) => {
    // 点击创建按钮
    await page.click('button:has-text("新建 Ticket")')
    
    // 填写表单
    await page.fill('input[placeholder="请输入 Ticket 标题"]', '带标签的 Ticket')
    
    // 选择标签
    await page.click('.el-select')
    await page.click('.el-select-dropdown__item:has-text("Python")')
    
    // 提交表单
    await page.click('button:has-text("确定")')
    
    // 验证成功提示
    await expect(page.locator('.el-message--success')).toBeVisible()
    
    // 验证 Ticket 已创建并显示标签
    await expect(page.locator('text=带标签的 Ticket')).toBeVisible()
    await expect(page.locator('.tag-badge:has-text("Python")')).toBeVisible()
  })

  test('按标签筛选 Ticket', async ({ page }) => {
    // 点击标签筛选器
    await page.click('.tag-filter')
    
    // 选择一个标签
    await page.click('.el-select-dropdown__item:has-text("Python")')
    
    // 等待筛选结果
    await page.waitForSelector('.ticket-item')
    
    // 验证筛选结果只包含指定标签的 Ticket
    const ticketItems = page.locator('.ticket-item')
    for (const item of await ticketItems.all()) {
      await expect(item.locator('.tag-badge:has-text("Python")')).toBeVisible()
    }
  })

  test('取消创建 Ticket', async ({ page }) => {
    // 点击创建按钮
    await page.click('button:has-text("新建 Ticket")')
    
    // 填写表单
    await page.fill('input[placeholder="请输入 Ticket 标题"]', '取消测试')
    
    // 点击取消按钮
    await page.click('button:has-text("取消")')
    
    // 验证对话框已关闭
    await expect(page.locator('.el-dialog')).not.toBeVisible()
    
    // 验证 Ticket 未创建
    await expect(page.locator('text=取消测试')).not.toBeVisible()
  })

  test('编辑时取消修改', async ({ page }) => {
    // 假设列表中有一个 Ticket
    const ticketItem = page.locator('.ticket-item').first()
    
    // 获取原始标题
    const originalTitle = await ticketItem.locator('.ticket-title').textContent()
    
    // 点击编辑按钮
    await ticketItem.locator('button:has-text("编辑")').click()
    
    // 修改标题
    await page.fill('input[placeholder="请输入 Ticket 标题"]', '修改后的标题')
    
    // 点击取消按钮
    await page.click('button:has-text("取消")')
    
    // 验证对话框已关闭
    await expect(page.locator('.el-dialog')).not.toBeVisible()
    
    // 验证标题未修改
    await expect(page.locator(`text=${originalTitle}`)).toBeVisible()
  })

  test('Ticket 标题长度验证', async ({ page }) => {
    // 点击创建按钮
    await page.click('button:has-text("新建 Ticket")')
    
    // 输入超过最大长度的标题
    await page.fill('input[placeholder="请输入 Ticket 标题"]', 'A'.repeat(201))
    
    // 验证字数统计
    await expect(page.locator('.el-input__count')).toContainText('201/200')
    
    // 尝试提交
    await page.click('button:has-text("确定")')
    
    // 验证显示验证错误
    await expect(page.locator('.el-form-item__error')).toBeVisible()
  })

  test('Ticket 描述长度验证', async ({ page }) => {
    // 点击创建按钮
    await page.click('button:has-text("新建 Ticket")')
    
    // 输入超过最大长度的描述
    await page.fill('textarea[placeholder="请输入 Ticket 描述"]', 'A'.repeat(2001))
    
    // 验证字数统计
    await expect(page.locator('.el-input__count')).toContainText('2001/2000')
  })

  test('批量删除 Ticket', async ({ page }) => {
    // 勾选多个 Ticket
    const checkboxes = page.locator('.ticket-item .el-checkbox__input')
    await checkboxes.nth(0).check()
    await checkboxes.nth(1).check()
    
    // 点击批量删除按钮
    await page.click('button:has-text("批量删除")')
    
    // 确认删除
    await page.click('.el-button--primary:has-text("确定")')
    
    // 验证成功提示
    await expect(page.locator('.el-message--success')).toBeVisible()
    
    // 验证 Ticket 已删除
    await expect(checkboxes.nth(0)).not.toBeChecked()
  })
})
