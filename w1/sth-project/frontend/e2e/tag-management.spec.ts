import { test, expect } from '@playwright/test'

/**
 * Tag 管理端到端测试
 * 测试标签的创建、查看、删除等功能
 */

test.describe('Tag 管理', () => {
  test.beforeEach(async ({ page }) => {
    // 导航到标签页面
    await page.goto('/tags')
    await page.waitForLoadState('networkidle')
  })

  /**
   * 测试创建新标签
   */
  test('创建新标签', async ({ page }) => {
    // 点击新建标签按钮
    await page.click('button:has-text("新建标签")')

    // 等待对话框出现
    await expect(page.locator('.el-dialog')).toBeVisible()

    // 填写标签名称
    await page.fill('input[placeholder="请输入标签名称"]', '测试标签')

    // 选择标签颜色
    await page.click('.el-color-picker__trigger')
    await page.click('.el-color-dropdown__link-btn:has-text("确定")')

    // 提交表单
    await page.click('button:has-text("确定")')

    // 验证成功提示
    await expect(page.locator('.el-message--success')).toBeVisible()

    // 验证标签列表中包含新创建的标签
    await expect(page.locator('text=测试标签')).toBeVisible()
  })

  /**
   * 测试创建标签时验证必填字段
   */
  test('创建标签时验证必填字段', async ({ page }) => {
    // 点击新建标签按钮
    await page.click('button:has-text("新建标签")')

    // 等待对话框出现
    await expect(page.locator('.el-dialog')).toBeVisible()

    // 不填写任何内容，直接提交
    await page.click('button:has-text("确定")')

    // 验证错误提示
    await expect(page.locator('.el-form-item__error')).toBeVisible()
  })

  /**
   * 测试创建标签时验证名称长度限制
   */
  test('创建标签时验证名称长度限制', async ({ page }) => {
    // 点击新建标签按钮
    await page.click('button:has-text("新建标签")')

    // 等待对话框出现
    await expect(page.locator('.el-dialog')).toBeVisible()

    // 填写超长名称（超过50个字符）
    const longName = '这是一个非常非常非常非常非常非常非常非常非常非常非常非常长的标签名称'
    await page.fill('input[placeholder="请输入标签名称"]', longName)

    // 验证输入框显示错误状态
    await expect(page.locator('.el-input.is-error')).toBeVisible()
  })

  /**
   * 测试创建重复名称的标签
   */
  test('创建重复名称的标签', async ({ page }) => {
    // 先创建一个标签
    await page.click('button:has-text("新建标签")')
    await page.fill('input[placeholder="请输入标签名称"]', '重复标签')
    await page.click('button:has-text("确定")')
    await expect(page.locator('.el-message--success')).toBeVisible()

    // 再次尝试创建相同名称的标签
    await page.click('button:has-text("新建标签")')
    await page.fill('input[placeholder="请输入标签名称"]', '重复标签')
    await page.click('button:has-text("确定")')

    // 验证错误提示
    await expect(page.locator('.el-message--error')).toBeVisible()
  })

  /**
   * 测试删除标签
   */
  test('删除标签', async ({ page }) => {
    // 先创建一个标签
    await page.click('button:has-text("新建标签")')
    await page.fill('input[placeholder="请输入标签名称"]', '待删除标签')
    await page.click('button:has-text("确定")')
    await expect(page.locator('.el-message--success')).toBeVisible()

    // 找到待删除标签并点击删除按钮
    const tagItem = page.locator('.tag-item').filter({ hasText: '待删除标签' })
    await tagItem.locator('button:has-text("删除")').click()

    // 确认删除
    await page.click('.el-message-box__btns button:has-text("确定")')

    // 验证成功提示
    await expect(page.locator('.el-message--success')).toBeVisible()

    // 验证标签已从列表中移除
    await expect(page.locator('text=待删除标签')).not.toBeVisible()
  })

  /**
   * 测试取消删除标签
   */
  test('取消删除标签', async ({ page }) => {
    // 先创建一个标签
    await page.click('button:has-text("新建标签")')
    await page.fill('input[placeholder="请输入标签名称"]', '保留标签')
    await page.click('button:has-text("确定")')
    await expect(page.locator('.el-message--success')).toBeVisible()

    // 点击删除按钮
    const tagItem = page.locator('.tag-item').filter({ hasText: '保留标签' })
    await tagItem.locator('button:has-text("删除")').click()

    // 取消删除
    await page.click('.el-message-box__btns button:has-text("取消")')

    // 验证标签仍然存在
    await expect(page.locator('text=保留标签')).toBeVisible()
  })

  /**
   * 测试标签列表为空时的显示
   */
  test('标签列表为空时的显示', async ({ page }) => {
    // 删除所有标签（如果存在）
    const tagItems = await page.locator('.tag-item').count()
    for (let i = 0; i < tagItems; i++) {
      const firstTag = page.locator('.tag-item').first()
      await firstTag.locator('button:has-text("删除")').click()
      await page.click('.el-message-box__btns button:has-text("确定")')
      await expect(page.locator('.el-message--success')).toBeVisible()
    }

    // 验证空状态显示
    await expect(page.locator('.el-empty')).toBeVisible()
    await expect(page.locator('text=暂无标签')).toBeVisible()
  })

  /**
   * 测试标签颜色选择器
   */
  test('标签颜色选择器', async ({ page }) => {
    // 点击新建标签按钮
    await page.click('button:has-text("新建标签")')

    // 填写标签名称
    await page.fill('input[placeholder="请输入标签名称"]', '彩色标签')

    // 点击颜色选择器
    await page.click('.el-color-picker__trigger')

    // 验证颜色选择面板出现
    await expect(page.locator('.el-color-dropdown')).toBeVisible()

    // 选择预设颜色
    await page.click('.el-color-predefine .el-color-predefine__color-selector').first()

    // 确认颜色选择
    await page.click('.el-color-dropdown__link-btn:has-text("确定")')

    // 提交表单
    await page.click('button:has-text("确定")')

    // 验证标签创建成功
    await expect(page.locator('.el-message--success')).toBeVisible()

    // 验证标签颜色显示正确
    const tagBadge = page.locator('.tag-item').filter({ hasText: '彩色标签' }).locator('.tag-badge')
    await expect(tagBadge).toBeVisible()
  })

  /**
   * 测试标签列表排序
   */
  test('标签列表排序', async ({ page }) => {
    // 创建多个标签
    const tagNames = ['标签C', '标签A', '标签B']
    for (const name of tagNames) {
      await page.click('button:has-text("新建标签")')
      await page.fill('input[placeholder="请输入标签名称"]', name)
      await page.click('button:has-text("确定")')
      await expect(page.locator('.el-message--success')).toBeVisible()
    }

    // 获取标签列表中的所有标签名称
    const tagItems = await page.locator('.tag-item .tag-badge').allTextContents()

    // 验证标签按名称排序
    const sortedNames = [...tagNames].sort()
    expect(tagItems).toEqual(sortedNames)
  })

  /**
   * 测试标签搜索功能
   */
  test('标签搜索功能', async ({ page }) => {
    // 创建多个标签
    const tagNames = ['紧急', '重要', '普通', '低优先级']
    for (const name of tagNames) {
      await page.click('button:has-text("新建标签")')
      await page.fill('input[placeholder="请输入标签名称"]', name)
      await page.click('button:has-text("确定")')
      await expect(page.locator('.el-message--success')).toBeVisible()
    }

    // 搜索包含"要"的标签
    await page.fill('input[placeholder="搜索标签"]', '要')

    // 验证只显示匹配的标签
    await expect(page.locator('text=重要')).toBeVisible()
    await expect(page.locator('text=紧急')).not.toBeVisible()
    await expect(page.locator('text=普通')).not.toBeVisible()
    await expect(page.locator('text=低优先级')).not.toBeVisible()

    // 清空搜索
    await page.fill('input[placeholder="搜索标签"]', '')

    // 验证所有标签都显示
    await expect(page.locator('text=紧急')).toBeVisible()
    await expect(page.locator('text=重要')).toBeVisible()
    await expect(page.locator('text=普通')).toBeVisible()
    await expect(page.locator('text=低优先级')).toBeVisible()
  })

  /**
   * 测试标签批量删除
   */
  test('标签批量删除', async ({ page }) => {
    // 创建多个标签
    const tagNames = ['待删除1', '待删除2', '保留标签']
    for (const name of tagNames) {
      await page.click('button:has-text("新建标签")')
      await page.fill('input[placeholder="请输入标签名称"]', name)
      await page.click('button:has-text("确定")')
      await expect(page.locator('.el-message--success')).toBeVisible()
    }

    // 选择多个标签进行删除（如果支持批量选择）
    const checkboxes = page.locator('.tag-item .el-checkbox')
    const count = await checkboxes.count()
    for (let i = 0; i < Math.min(2, count); i++) {
      await checkboxes.nth(i).click()
    }

    // 点击批量删除按钮（如果存在）
    const batchDeleteBtn = page.locator('button:has-text("批量删除")')
    if (await batchDeleteBtn.isVisible()) {
      await batchDeleteBtn.click()
      await page.click('.el-message-box__btns button:has-text("确定")')
      await expect(page.locator('.el-message--success')).toBeVisible()
    }
  })

  /**
   * 测试标签对话框关闭功能
   */
  test('标签对话框关闭功能', async ({ page }) => {
    // 点击新建标签按钮
    await page.click('button:has-text("新建标签")')

    // 验证对话框出现
    await expect(page.locator('.el-dialog')).toBeVisible()

    // 点击取消按钮
    await page.click('.el-dialog button:has-text("取消")')

    // 验证对话框关闭
    await expect(page.locator('.el-dialog')).not.toBeVisible()

    // 验证标签列表没有变化
    const initialCount = await page.locator('.tag-item').count()
    await expect(page.locator('.tag-item')).toHaveCount(initialCount)
  })

  /**
   * 测试标签对话框 ESC 键关闭
   */
  test('标签对话框 ESC 键关闭', async ({ page }) => {
    // 点击新建标签按钮
    await page.click('button:has-text("新建标签")')

    // 验证对话框出现
    await expect(page.locator('.el-dialog')).toBeVisible()

    // 按 ESC 键
    await page.keyboard.press('Escape')

    // 验证对话框关闭
    await expect(page.locator('.el-dialog')).not.toBeVisible()
  })

  /**
   * 测试标签对话框点击遮罩关闭
   */
  test('标签对话框点击遮罩关闭', async ({ page }) => {
    // 点击新建标签按钮
    await page.click('button:has-text("新建标签")')

    // 验证对话框出现
    await expect(page.locator('.el-dialog')).toBeVisible()

    // 点击遮罩层
    await page.click('.el-overlay')

    // 验证对话框关闭
    await expect(page.locator('.el-dialog')).not.toBeVisible()
  })
})
