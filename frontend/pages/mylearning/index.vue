<template>
	<view class="container">
		<scroll-view class="content" scroll-y>
			<!-- 用户信息卡片 -->
			<view class="profile-card" @click="goToProfile">
				<view class="profile-info">
					<view class="avatar-wrapper-small">
						<image 
							v-if="userProfile.avatar" 
							:src="getAvatarUrl(userProfile.avatar)" 
							class="avatar-small"
							mode="aspectFill"
						/>
						<view v-else class="avatar-placeholder-small">
							<text class="avatar-text-small">{{ userProfile.nickname || userProfile.username || '我' }}</text>
						</view>
					</view>
					<view class="profile-text">
						<text class="profile-name">{{ userProfile.nickname || userProfile.username || '未设置昵称' }}</text>
						<text class="profile-subtitle">点击查看个人资料</text>
					</view>
				</view>
				<text class="arrow-icon">›</text>
			</view>

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
							<text class="info-text" v-if="publicInfo.grade">{{ publicInfo.grade }} · {{ publicInfo.version }} · {{ publicInfo.unit }}</text>
							<text class="info-text" v-else>尚未开始练习</text>
							<text class="info-text" v-if="publicInfo.total > 0">已完成 {{ publicInfo.completed }} / {{ publicInfo.total }} 题</text>
							<text class="info-text time" v-if="publicInfo.lastTime">最近练习：{{ publicInfo.lastTime }}</text>
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
							<text class="info-text" v-if="internationalInfo.level">当前水平：{{ internationalInfo.level }}</text>
							<text class="info-text" v-else>尚未完成分级测试</text>
							<text class="info-text" v-if="internationalInfo.modules > 0">学习模块：{{ internationalInfo.modules }} 个</text>
							<text class="info-text time" v-if="internationalInfo.lastTime">最近对话：{{ internationalInfo.lastTime }}</text>
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
	import { getProfile, getLearningStats, getWrongBookList, getWordBookList } from '@/utils/api.js'

	export default {
		data() {
			return {
				userProfile: {
					username: '',
					nickname: null,
					avatar: null
				},
				weekDays: [
					{ practiced: false },
					{ practiced: false },
					{ practiced: false },
					{ practiced: false },
					{ practiced: false },
					{ practiced: false },
					{ practiced: false }
				],
				totalQuestions: 0,
				publicInfo: {
					grade: '',
					version: '',
					unit: '',
					completed: 0,
					total: 0,
					lastTime: ''
				},
				internationalInfo: {
					level: '',
					modules: 0,
					lastTime: ''
				},
				wrongBookCount: 0,
				wordBookCount: 0
			}
		},
		onShow() {
			// tabBar页面每次显示时刷新数据
			this.loadData()
			this.loadUserProfile()
		},
		methods: {
			async loadUserProfile() {
				const token = uni.getStorageSync('token')
				if (token) {
					try {
						const profile = await getProfile()
						this.userProfile = profile
					} catch (error) {
						console.error('加载用户资料失败:', error)
						// 如果是401错误，可能是token过期
						if (error.statusCode === 401) {
							// 清理过期的token
							uni.removeStorageSync('token')
							// 从本地存储获取基本信息作为fallback
							const currentUser = uni.getStorageSync('currentUser')
							if (currentUser) {
								this.userProfile = {
									username: currentUser.username || '',
									nickname: currentUser.nickname || null,
									avatar: currentUser.avatar || null
								}
							}
						} else {
							// 其他错误，从本地存储获取基本信息
							const currentUser = uni.getStorageSync('currentUser')
							if (currentUser) {
								this.userProfile = {
									username: currentUser.username || '',
									nickname: currentUser.nickname || null,
									avatar: currentUser.avatar || null
								}
							}
						}
					}
				} else {
					// 未登录，从本地存储获取基本信息
					const currentUser = uni.getStorageSync('currentUser')
					if (currentUser) {
						this.userProfile = {
							username: currentUser.username || '',
							nickname: currentUser.nickname || null,
							avatar: currentUser.avatar || null
						}
					}
				}
			},
			getAvatarUrl(avatar) {
				if (!avatar) return ''
				if (avatar.startsWith('http')) {
					return avatar
				}
				return `http://127.0.0.1:8000${avatar}`
			},
			goToProfile() {
				uni.switchTab({
					url: '/pages/profile/index'
				})
			},
			formatTime(timeStr) {
				if (!timeStr) return ''
				const time = new Date(timeStr)
				const now = new Date()
				const diff = now - time
				const minutes = Math.floor(diff / 60000)
				const hours = Math.floor(minutes / 60)
				const days = Math.floor(hours / 24)
				
				if (days > 0) {
					return `${days}天前`
				} else if (hours > 0) {
					return `${hours}小时前`
				} else if (minutes > 0) {
					return `${minutes}分钟前`
				} else {
					return '刚刚'
				}
			},
			async loadData() {
				const token = uni.getStorageSync('token')
				if (!token) {
					return
				}
				
				try {
					// 获取学习统计
					const stats = await getLearningStats()
					this.weekDays = (stats.week_days || []).map(practiced => ({ practiced }))
					this.totalQuestions = stats.total_questions || 0
					
					// 更新公立模式信息
					if (stats.public_info) {
						this.publicInfo = {
							grade: stats.public_info.grade || '',
							version: stats.public_info.version || '',
							unit: stats.public_info.unit || '',
							completed: stats.public_info.completed || 0,
							total: stats.public_info.total || 0,
							lastTime: this.formatTime(stats.public_info.last_practice_time)
						}
					}
					
					// 更新国际模式信息
					if (stats.international_info) {
						this.internationalInfo = {
							level: stats.international_info.level || '',
							modules: stats.international_info.modules_count || 0,
							lastTime: this.formatTime(stats.international_info.last_conversation_time)
						}
					}
					
					// 获取错题本数量
					try {
						const wrongBookResult = await getWrongBookList(1, 1)
						this.wrongBookCount = wrongBookResult.total || 0
					} catch (e) {
						console.error('获取错题本失败:', e)
					}
					
					// 获取生词本数量
					try {
						const wordBookResult = await getWordBookList(1, 1)
						this.wordBookCount = wordBookResult.total || 0
					} catch (e) {
						console.error('获取生词本失败:', e)
					}
				} catch (error) {
					console.error('加载学习数据失败:', error)
					if (error.statusCode === 401) {
						uni.removeStorageSync('token')
					}
				}
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
				uni.showToast({
					title: '错题本功能开发中',
					icon: 'none'
				})
			},
			reviewWrongBook() {
				// 跳转到国际模式 AI 教练，并自动发送提示
				uni.navigateTo({
					url: '/pages/international/path'
				})
				// 可以通过事件总线或全局状态传递提示词
			},
			openWordBook() {
				uni.showToast({
					title: '生词本功能开发中',
					icon: 'none'
				})
			},
			reviewWords() {
				uni.showToast({
					title: '生词复习功能开发中',
					icon: 'none'
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

	.profile-card {
		background-color: #FFFFFF;
		border-radius: 24rpx;
		padding: 30rpx 40rpx;
		margin-bottom: 40rpx;
		box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.profile-info {
		display: flex;
		align-items: center;
		flex: 1;
	}

	.avatar-wrapper-small {
		width: 100rpx;
		height: 100rpx;
		border-radius: 50%;
		overflow: hidden;
		margin-right: 24rpx;
		background-color: #F5F5F5;
	}

	.avatar-small {
		width: 100%;
		height: 100%;
	}

	.avatar-placeholder-small {
		width: 100%;
		height: 100%;
		background-color: #2F5D62;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.avatar-text-small {
		color: #FFFFFF;
		font-size: 32rpx;
		font-weight: 500;
	}

	.profile-text {
		flex: 1;
		display: flex;
		flex-direction: column;
	}

	.profile-name {
		font-size: 32rpx;
		font-weight: 500;
		color: #2F5D62;
		margin-bottom: 8rpx;
	}

	.profile-subtitle {
		font-size: 24rpx;
		color: #999;
	}

	.arrow-icon {
		font-size: 48rpx;
		color: #B0B0B0;
		margin-left: 20rpx;
	}
</style>

