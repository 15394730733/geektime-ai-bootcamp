/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./node_modules/@refinedev/ui/src/**/*.{js,ts,jsx,tsx}",
    "./node_modules/@refinedev/antd/src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e6f7ff',
          100: '#bae7ff',
          500: '#1890ff',
          600: '#096dd9',
          700: '#0050b3',
        }
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
        mono: ['SFMono-Regular', 'Consolas', 'Liberation Mono', 'Menlo', 'Courier', 'monospace'],
      }
    },
  },
  plugins: [],
  // 禁用可能冲突的 preflight 样式
  corePlugins: {
    preflight: false,
  },
  // Tailwind CSS v4 兼容性配置
  future: {
    hoverOnlyWhenSupported: true,
  },
}
