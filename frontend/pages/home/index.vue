<template>
	<view class="container">
		<!-- 自定义导航栏 -->
		<view class="custom-navbar">
			<view class="navbar-content">
				<text class="main-title">AI English Lab</text>
				<text class="sub-title">找到适合你的英语学习路径</text>
			</view>
		</view>

		<!-- 页面内容 -->
		<scroll-view class="content" scroll-y>
			<!-- 区块1：欢迎文案 -->
			<view class="welcome-section">
				<text class="welcome-title">Choose Your Learning Path</text>
				<text class="welcome-desc">公立学校模式打好基础，国际学校模式全方位进阶，由 AI 为你定制学习。</text>
				<view class="auth-buttons" v-if="!isLoggedIn">
					<button class="auth-btn register-btn" @click="goToRegister">创建账号</button>
					<button class="auth-btn login-btn" @click="goToLogin">登录</button>
				</view>
			</view>

			<!-- 区块2：两张大卡片 -->
			<view class="cards-container">
				<!-- 卡片1：公立学校模式 -->
				<view class="mode-card" @click="goToPublicMode">
					<view class="card-header">
						<text class="card-title">公立学校模式</text>
						<text class="card-subtitle">按年级与教材，打牢词汇与语法基础</text>
					</view>
					<view class="card-features">
						<view class="feature-item">
							<text class="feature-icon">📚</text>
							<text class="feature-text">告诉我你几年级</text>
						</view>
						<view class="feature-item">
							<text class="feature-icon">📖</text>
							<text class="feature-text">按教材单元精准出题</text>
						</view>
						<view class="feature-item">
							<text class="feature-icon">📝</text>
							<text class="feature-text">错题本巩固基础</text>
						</view>
					</view>
					<view class="card-footer">
						<button class="primary-btn" @click.stop="goToPublicMode">进入公立模式</button>
					</view>
				</view>

				<!-- 卡片2：国际学校模式 -->
				<view class="mode-card" @click="goToInternationalMode">
					<view class="card-header">
						<text class="card-title">国际学校模式</text>
						<text class="card-subtitle">分级测试 + AI 路径规划，全面提升听说读写</text>
					</view>
					<view class="card-features">
						<view class="feature-item">
							<text class="feature-icon">🎯</text>
							<text class="feature-text">先做一次分级测试</text>
						</view>
						<view class="feature-item">
							<text class="feature-icon">🤖</text>
							<text class="feature-text">AI 推荐你该学什么</text>
						</view>
						<view class="feature-item">
							<text class="feature-icon">✍️</text>
							<text class="feature-text">写作批改 + 口语训练</text>
						</view>
					</view>
					<view class="card-footer">
						<button class="primary-btn" @click.stop="goToInternationalMode">进入国际模式</button>
					</view>
				</view>
			</view>
		</scroll-view>
	</view>
</template>

<script>
	import { getProfile } from '@/utils/api.js'
	
	export default {
		data() {
			return {
				isLoggedIn: false
			}
		},
		onLoad() {
			this.checkLoginStatus()
		},
		methods: {
			async checkLoginStatus() {
				const token = uni.getStorageSync('token')
				if (token) {
					try {
						await getProfile()
						this.isLoggedIn = true
					} catch (error) {
						this.isLoggedIn = false
						uni.removeStorageSync('token')
					}
				} else {
					this.isLoggedIn = false
				}
			},
			goToPublicMode() {
				uni.switchTab({
					url: '/pages/public/grade-select'
				})
			},
			goToInternationalMode() {
				uni.switchTab({
					url: '/pages/international/test'
				})
			},
			goToRegister() {
				uni.navigateTo({
					url: '/pages/auth/register'
				})
			},
			goToLogin() {
				uni.navigateTo({
					url: '/pages/auth/login'
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

	.custom-navbar {
		padding: 60rpx 40rpx 40rpx;
		background-color: #F8F6F2;
		width: 100%;
		box-sizing: border-box;
	}

	.navbar-content {
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
		width: 100%;
	}

	.main-title {
		font-size: 48rpx;
		font-weight: 300;
		color: #2F5D62;
		letter-spacing: 2rpx;
		margin-bottom: 16rpx;
	}

	.sub-title {
		font-size: 26rpx;
		color: #B0B0B0;
		font-weight: 300;
	}

	.content {
		flex: 1;
		padding: 0 40rpx 40rpx;
		width: 100%;
		box-sizing: border-box;
	}

	.welcome-section {
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
		margin-bottom: 80rpx;
		padding-top: 40rpx;
	}

	.welcome-title {
		font-size: 56rpx;
		font-weight: 300;
		color: #2F5D62;
		margin-bottom: 32rpx;
		letter-spacing: 1rpx;
	}

	.welcome-desc {
		font-size: 28rpx;
		color: #666;
		line-height: 1.8;
		max-width: 600rpx;
		margin-bottom: 40rpx;
	}

	.auth-buttons {
		display: flex;
		gap: 20rpx;
		margin-top: 40rpx;
	}

	.auth-btn {
		padding: 16rpx 32rpx;
		border-radius: 50rpx;
		font-size: 26rpx;
		border: none;
	}

	.register-btn {
		background-color: #2F5D62;
		color: #FFFFFF;
		box-shadow: 0 4rpx 12rpx rgba(47, 93, 98, 0.2);
	}

	.login-btn {
		background-color: transparent;
		color: #2F5D62;
		border: 2rpx solid #2F5D62 !important;
	}

	.auth-btn:active {
		opacity: 0.8;
	}

	.cards-container {
		display: flex;
		flex-direction: column;
		gap: 40rpx;
	}

	.mode-card {
		background-color: #FFFFFF;
		border-radius: 24rpx;
		padding: 48rpx 40rpx;
		box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
		border: 1rpx solid #F0F0F0;
		transition: all 0.3s ease;
	}

	.mode-card:active {
		transform: translateY(-4rpx);
		box-shadow: 0 8rpx 30rpx rgba(0, 0, 0, 0.08);
	}

	.card-header {
		margin-bottom: 40rpx;
	}

	.card-title {
		display: block;
		font-size: 40rpx;
		font-weight: 400;
		color: #2F5D62;
		margin-bottom: 16rpx;
	}

	.card-subtitle {
		display: block;
		font-size: 26rpx;
		color: #999;
		line-height: 1.6;
	}

	.card-features {
		margin-bottom: 40rpx;
	}

	.feature-item {
		display: flex;
		align-items: center;
		margin-bottom: 24rpx;
	}

	.feature-icon {
		font-size: 32rpx;
		margin-right: 16rpx;
	}

	.feature-text {
		font-size: 28rpx;
		color: #666;
	}

	.card-footer {
		display: flex;
		justify-content: flex-end;
		margin-top: 20rpx;
	}

	.primary-btn {
		background-color: #2F5D62;
		color: #FFFFFF;
		border: none;
		border-radius: 50rpx;
		padding: 20rpx 48rpx;
		font-size: 28rpx;
		font-weight: 400;
		box-shadow: 0 4rpx 12rpx rgba(47, 93, 98, 0.2);
	}

	.primary-btn:active {
		opacity: 0.8;
	}
</style>

