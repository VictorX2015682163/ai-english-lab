<template>
	<view class="container">
		<scroll-view class="content" scroll-y>
			<!-- 顶部标题 -->
			<view class="header-section">
				<text class="main-title">我的学习</text>
				<text class="sub-title">一眼看到你的基础练习与进阶提升</text>
			</view>

			<!-- 学习概览 -->
			<view class="summary-section">
				<view class="summary-item">
					<text class="summary-label">本周练习天数</text>
					<view class="week-dots">
						<view 
							v-for="(day, index) in weekDays" 
							:key="index"
							class="week-dot"
							:class="{ active: day.practiced }"
						></view>
					</view>
				</view>
				<view class="summary-item">
					<text class="summary-label">累计完成题目</text>
					<text class="summary-value">{{ totalQuestions }}</text>
				</view>
			</view>

			<!-- 主要卡片 -->
			<view class="main-cards">
				<!-- 公立学校模式学习卡 -->
				<view class="learning-card">
					<view class="card-icon">📚</view>
					<view class="card-content">
						<text class="card-title">公立学校模式</text>
						<view class="card-info">
							<text class="info-text">{{ publicInfo.grade }} · {{ publicInfo.version }} · {{ publicInfo.unit }}</text>
							<text class="info-text">已完成 {{ publicInfo.completed }} / {{ publicInfo.total }} 题</text>
							<text class="info-text time">最近练习：{{ publicInfo.lastTime }}</text>
						</view>
						<button class="continue-btn" @click="continuePublic">继续公立模式练习</button>
					</view>
				</view>

				<!-- 国际学校模式学习卡 -->
				<view class="learning-card">
					<view class="card-icon">🌍</view>
					<view class="card-content">
						<text class="card-title">国际学校模式</text>
						<view class="card-info">
							<text class="info-text">当前水平：{{ internationalInfo.level }}</text>
							<text class="info-text">学习模块：{{ internationalInfo.modules }} 个</text>
							<text class="info-text time">最近对话：{{ internationalInfo.lastTime }}</text>
						</view>
						<button class="continue-btn" @click="continueInternational">继续国际模式学习</button>
					</view>
				</view>
			</view>

			<!-- 错题本 & 生词本 -->
			<view class="bottom-cards">
				<view class="small-card" @click="openWrongBook">
					<view class="small-card-header">
						<text class="small-card-title">错题本</text>
						<text class="small-card-count">{{ wrongBookCount }} 题</text>
					</view>
					<button class="small-card-btn" @click.stop="reviewWrongBook">让 AI 再考我一次</button>
				</view>

				<view class="small-card" @click="openWordBook">
					<view class="small-card-header">
						<text class="small-card-title">生词本</text>
						<text class="small-card-count">{{ wordBookCount }} 词</text>
					</view>
					<button class="small-card-btn" @click.stop="reviewWords">进入生词复习</button>
				</view>
			</view>
		</scroll-view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				weekDays: [
					{ practiced: true },
					{ practiced: true },
					{ practiced: false },
					{ practiced: true },
					{ practiced: true },
					{ practiced: false },
					{ practiced: false }
				],
				totalQuestions: 45,
				publicInfo: {
					grade: '六年级',
					version: '人教版',
					unit: 'Unit 3',
					completed: 12,
					total: 20,
					lastTime: '2小时前'
				},
				internationalInfo: {
					level: 'B1 Intermediate',
					modules: 2,
					lastTime: '昨天'
				},
				wrongBookCount: 5,
				wordBookCount: 23
			}
		},
		onLoad() {
			this.loadData()
		},
		onShow() {
			this.loadData()
		},
		methods: {
			loadData() {
				// 从本地存储加载数据
				const practiceInfo = uni.getStorageSync('practiceInfo')
				if (practiceInfo) {
					this.publicInfo = {
						...this.publicInfo,
						...practiceInfo
					}
				}

				const testResult = uni.getStorageSync('testResult')
				if (testResult) {
					this.internationalInfo.level = testResult.level
				}

				const wrongBook = uni.getStorageSync('wrongBook') || []
				// 过滤有效错题
				const validWrongs = wrongBook.filter(w => w && w.question && w.correctAnswer)
				this.wrongBookCount = validWrongs.length

				const wordBook = uni.getStorageSync('wordBook') || []
				this.wordBookCount = wordBook.length
			},
			continuePublic() {
				// 如果有练习信息，直接进入练习页，否则进入选择页
				const practiceInfo = uni.getStorageSync('practiceInfo')
				if (practiceInfo) {
					uni.navigateTo({
						url: '/pages/public/practice'
					})
				} else {
					uni.switchTab({
						url: '/pages/public/grade-select'
					})
				}
			},
			continueInternational() {
				uni.navigateTo({
					url: '/pages/international/path'
				})
			},
			openWrongBook() {
				uni.navigateTo({
					url: '/pages/mylearning/wrong-book'
				})
			},
			reviewWrongBook() {
				const wrongBook = uni.getStorageSync('wrongBook') || []
				if (wrongBook.length === 0) {
					uni.showToast({
						title: '错题本为空，请先做练习',
						icon: 'none',
						duration: 2000
					})
					return
				}
				uni.navigateTo({
					url: '/pages/mylearning/wrong-review'
				})
			},
			openWordBook() {
				uni.navigateTo({
					url: '/pages/mylearning/word-book'
				})
			},
			reviewWords() {
				const wordBook = uni.getStorageSync('wordBook') || []
				if (wordBook.length === 0) {
					uni.showToast({
						title: '生词本为空，请先添加生词',
						icon: 'none',
						duration: 2000
					})
					return
				}
				uni.navigateTo({
					url: '/pages/mylearning/word-review'
				})
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
		flex: 1;
		padding: 40rpx;
		width: 100%;
		box-sizing: border-box;
	}

	.header-section {
		text-align: center;
		margin-bottom: 60rpx;
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
	}

	.summary-section {
		background-color: #FFFFFF;
		border-radius: 24rpx;
		padding: 40rpx;
		margin-bottom: 40rpx;
		box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
	}

	.summary-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 32rpx;
	}

	.summary-item:last-child {
		margin-bottom: 0;
	}

	.summary-label {
		font-size: 28rpx;
		color: #666;
	}

	.week-dots {
		display: flex;
		gap: 16rpx;
	}

	.week-dot {
		width: 24rpx;
		height: 24rpx;
		border-radius: 50%;
		background-color: #E0E0E0;
	}

	.week-dot.active {
		background-color: #2F5D62;
	}

	.summary-value {
		font-size: 36rpx;
		font-weight: 500;
		color: #2F5D62;
	}

	.main-cards {
		display: flex;
		flex-direction: column;
		gap: 32rpx;
		margin-bottom: 40rpx;
	}

	.learning-card {
		background-color: #FFFFFF;
		border-radius: 24rpx;
		padding: 40rpx;
		box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
		display: flex;
		align-items: flex-start;
	}

	.card-icon {
		font-size: 64rpx;
		margin-right: 24rpx;
	}

	.card-content {
		flex: 1;
	}

	.card-title {
		display: block;
		font-size: 32rpx;
		font-weight: 500;
		color: #2F5D62;
		margin-bottom: 24rpx;
	}

	.card-info {
		margin-bottom: 32rpx;
	}

	.info-text {
		display: block;
		font-size: 26rpx;
		color: #666;
		margin-bottom: 12rpx;
		line-height: 1.6;
	}

	.info-text.time {
		color: #999;
		font-size: 24rpx;
	}

	.continue-btn {
		width: 100%;
		background-color: #2F5D62;
		color: #FFFFFF;
		border: none;
		border-radius: 50rpx;
		padding: 20rpx;
		font-size: 28rpx;
		box-shadow: 0 4rpx 12rpx rgba(47, 93, 98, 0.2);
	}

	.bottom-cards {
		display: flex;
		gap: 24rpx;
	}

	.small-card {
		flex: 1;
		background-color: #FFFFFF;
		border-radius: 24rpx;
		padding: 32rpx;
		box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
	}

	.small-card-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 24rpx;
	}

	.small-card-title {
		font-size: 28rpx;
		font-weight: 500;
		color: #2F5D62;
	}

	.small-card-count {
		font-size: 24rpx;
		color: #999;
	}

	.small-card-btn {
		width: 100%;
		background-color: transparent;
		border: 2rpx solid #2F5D62;
		color: #2F5D62;
		border-radius: 50rpx;
		padding: 16rpx;
		font-size: 26rpx;
	}
</style>

