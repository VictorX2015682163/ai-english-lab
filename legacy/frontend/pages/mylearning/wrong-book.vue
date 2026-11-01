<template>
	<view class="container">
		<view class="content">
			<!-- 顶部标题栏 -->
			<view class="header-section">
				<text class="main-title">错题本</text>
				<text class="sub-title">共 {{ wrongList.length }} 道错题</text>
				<button class="test-btn" @click="testLoad">测试加载</button>
			</view>

			<!-- 错题列表 -->
			<view class="wrong-list" v-if="wrongList.length > 0">
				<view 
					v-for="(item, index) in wrongList" 
					:key="item.id || item.time || index"
					class="wrong-item"
				>
					<view class="wrong-content">
						<view class="wrong-header">
							<text class="wrong-type">{{ item.type === 'choice' ? '选择题' : '填空题' }}</text>
							<text class="wrong-time">{{ formatTime(item.time) }}</text>
						</view>
						<text class="wrong-question">{{ item.question }}</text>
						<view class="wrong-answer-section">
							<view class="answer-row">
								<text class="answer-label">你的答案：</text>
								<text class="answer-value wrong-answer">{{ item.userAnswer || '未作答' }}</text>
							</view>
							<view class="answer-row">
								<text class="answer-label">正确答案：</text>
								<text class="answer-value correct-answer">{{ item.correctAnswer }}</text>
							</view>
						</view>
						<text class="wrong-explanation" v-if="item.explanation">{{ item.explanation }}</text>
					</view>
					<view class="wrong-actions">
						<button class="action-btn delete-btn" @click="deleteWrong(item)">删除</button>
					</view>
				</view>
			</view>

			<!-- 空状态 -->
			<view class="empty-state" v-else>
				<text class="empty-icon">📝</text>
				<text class="empty-text">还没有错题</text>
				<text class="empty-desc">做错题目并加入错题本后，会显示在这里</text>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				wrongList: []
			}
		},
		onLoad() {
			this.loadWrongs()
		},
		onShow() {
			// 每次显示页面时重新加载，确保数据最新
			this.loadWrongs()
		},
		methods: {
			loadWrongs() {
				const wrongs = uni.getStorageSync('wrongBook') || []
				
				if (wrongs.length === 0) {
					this.wrongList = []
					uni.showToast({
						title: '错题本为空',
						icon: 'none',
						duration: 1500
					})
					return
				}
				
				// 过滤无效数据并按时间倒序排列
				const filtered = wrongs.filter(w => {
					return w && w.question && w.correctAnswer
				})
				
				this.wrongList = filtered.sort((a, b) => {
					const timeA = a.time ? new Date(a.time).getTime() : 0
					const timeB = b.time ? new Date(b.time).getTime() : 0
					return timeB - timeA
				})
				
				// 如果过滤后数量为0，但原始数据不为0，说明数据格式有问题
				if (filtered.length === 0 && wrongs.length > 0) {
					uni.showModal({
						title: '数据格式异常',
						content: `原始数据有 ${wrongs.length} 条，但过滤后为0条。请检查数据格式。`,
						showCancel: false
					})
				}
			},
			testLoad() {
				const wrongs = uni.getStorageSync('wrongBook') || []
				uni.showModal({
					title: '调试信息',
					content: `存储的错题数量: ${wrongs.length}\n显示的数量: ${this.wrongList.length}\n原始数据: ${JSON.stringify(wrongs).substring(0, 200)}...`,
					showCancel: false
				})
			},
			deleteWrong(item) {
				uni.showModal({
					title: '确认删除',
					content: '确定要删除这道错题吗？',
					success: (res) => {
						if (res.confirm) {
							const wrongs = uni.getStorageSync('wrongBook') || []
							// 通过 id 或 time 找到要删除的项
							const itemId = item.id || item.time
							const index = wrongs.findIndex(w => (w.id || w.time) === itemId)
							if (index !== -1) {
								wrongs.splice(index, 1)
								uni.setStorageSync('wrongBook', wrongs)
								this.loadWrongs()
								uni.showToast({
									title: '已删除',
									icon: 'success'
								})
							}
						}
					}
				})
			},
			formatTime(timeStr) {
				if (!timeStr) return ''
				const date = new Date(timeStr)
				const now = new Date()
				const diff = now - date
				const days = Math.floor(diff / (1000 * 60 * 60 * 24))
				
				if (days === 0) {
					const hours = Math.floor(diff / (1000 * 60 * 60))
					if (hours === 0) {
						const minutes = Math.floor(diff / (1000 * 60))
						return minutes <= 0 ? '刚刚' : `${minutes}分钟前`
					}
					return `${hours}小时前`
				} else if (days === 1) {
					return '昨天'
				} else if (days < 7) {
					return `${days}天前`
				} else {
					return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
				}
			}
		}
	}
</script>

<style scoped>
	.container {
		min-height: 100vh;
		background-color: #F8F6F2;
		width: 100%;
		box-sizing: border-box;
	}

	.content {
		padding: 40rpx;
		width: 100%;
		box-sizing: border-box;
	}

	.header-section {
		text-align: center;
		margin-bottom: 40rpx;
	}

	.main-title {
		display: block;
		font-size: 44rpx;
		font-weight: 400;
		color: #2F5D62;
		margin-bottom: 16rpx;
	}

	.sub-title {
		display: block;
		font-size: 26rpx;
		color: #B0B0B0;
		margin-bottom: 16rpx;
	}

	.test-btn {
		margin-top: 16rpx;
		padding: 12rpx 24rpx;
		background-color: #2F5D62;
		color: #FFFFFF;
		border: none;
		border-radius: 20rpx;
		font-size: 24rpx;
	}

	.wrong-list {
		display: flex;
		flex-direction: column;
		gap: 24rpx;
	}

	.wrong-item {
		background-color: #FFFFFF;
		border-radius: 24rpx;
		padding: 32rpx;
		box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
	}

	.wrong-content {
		flex: 1;
	}

	.wrong-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 16rpx;
	}

	.wrong-type {
		font-size: 24rpx;
		color: #2F5D62;
		background-color: #F0F7F8;
		padding: 6rpx 12rpx;
		border-radius: 8rpx;
	}

	.wrong-time {
		font-size: 24rpx;
		color: #999;
	}

	.wrong-question {
		display: block;
		font-size: 28rpx;
		color: #333;
		line-height: 1.6;
		margin-bottom: 20rpx;
	}

	.wrong-answer-section {
		margin-bottom: 16rpx;
	}

	.answer-row {
		display: flex;
		align-items: center;
		margin-bottom: 12rpx;
	}

	.answer-label {
		font-size: 26rpx;
		color: #666;
		margin-right: 12rpx;
	}

	.answer-value {
		font-size: 26rpx;
		font-weight: 500;
	}

	.wrong-answer {
		color: #FF5252;
	}

	.correct-answer {
		color: #4CAF50;
	}

	.wrong-explanation {
		display: block;
		font-size: 26rpx;
		color: #999;
		line-height: 1.6;
		padding: 16rpx;
		background-color: #F5F5F5;
		border-radius: 12rpx;
	}

	.wrong-actions {
		display: flex;
		flex-direction: column;
		gap: 12rpx;
		margin-left: 24rpx;
	}

	.action-btn {
		padding: 12rpx 24rpx;
		border-radius: 20rpx;
		font-size: 24rpx;
		border: none;
	}

	.delete-btn {
		background-color: #FFE5E5;
		color: #FF5252;
	}

	.empty-state {
		text-align: center;
		padding: 120rpx 40rpx;
	}

	.empty-icon {
		display: block;
		font-size: 120rpx;
		margin-bottom: 32rpx;
	}

	.empty-text {
		display: block;
		font-size: 32rpx;
		color: #666;
		margin-bottom: 16rpx;
	}

	.empty-desc {
		display: block;
		font-size: 26rpx;
		color: #999;
	}
</style>

