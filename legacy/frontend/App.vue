<script>
	export default {
		onLaunch: function() {
			console.log('App Launch')
		},
		onShow: function() {
			console.log('App Show')
		},
		onHide: function() {
			console.log('App Hide')
		}
	}
</script>

<style>
	/*每个页面公共css */
	page {
		background-color: #F8F6F2;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
		box-sizing: border-box;
		width: 100%;
		margin: 0;
		padding: 0;
	}

	* {
		box-sizing: border-box;
	}

	/* 全局按钮样式重置 */
	button {
		font-size: 28rpx;
		line-height: 1.5;
		box-sizing: border-box;
		margin: 0;
		padding: 0;
	}

	button::after {
		border: none;
	}

	/* 全局输入框样式 */
	input {
		font-size: 28rpx;
		box-sizing: border-box;
		margin: 0;
		-webkit-appearance: none;
		appearance: none;
		background-color: transparent;
	}
	
	/* 确保输入框可以正常交互 */
	input:not([disabled]):not([readonly]) {
		cursor: text;
	}

	/* 全局滚动条样式 */
	::-webkit-scrollbar {
		width: 0;
		background: transparent;
	}

	/* 确保容器不偏移 */
	view, scroll-view {
		box-sizing: border-box;
	}

	/* 重置 body 和 html 的默认样式 */
	body, html {
		margin: 0;
		padding: 0;
		width: 100%;
		overflow-x: hidden;
	}
</style>
