<template>
	<view class="container">
		<view class="content">
			<!-- 顶部标题 -->
			<view class="header-section">
				<text class="main-title">登录</text>
				<text class="sub-title">欢迎回来</text>
			</view>

			<!-- 登录表单 -->
			<view class="form-card">
				<view class="form-group">
					<text class="form-label">用户名或邮箱</text>
					<input 
						class="form-input" 
						type="text"
						v-model="formData.username"
						placeholder="请输入用户名或邮箱"
						placeholder-style="color: #B0B0B0"
						:disabled="false"
						:readonly="false"
					/>
				</view>

				<view class="form-group">
					<text class="form-label">密码</text>
					<input 
						class="form-input" 
						type="password"
						v-model="formData.password"
						placeholder="请输入密码"
						placeholder-style="color: #B0B0B0"
						:password="true"
						:disabled="false"
						:readonly="false"
					/>
				</view>

				<button class="submit-btn" @click="handleLogin" :disabled="!canSubmit">
					登录
				</button>

				<view class="register-link">
					<text class="link-text">还没有账号？</text>
					<text class="link-btn" @click="goToRegister">立即注册</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				formData: {
					username: '',
					password: ''
				}
			}
		},
		computed: {
			canSubmit() {
				return this.formData.username.length > 0 && this.formData.password.length > 0
			}
		},
		methods: {
			handleLogin() {
				if (!this.canSubmit) {
					uni.showToast({
						title: '请填写完整信息',
						icon: 'none'
					})
					return
				}

				// 获取所有用户
				const users = uni.getStorageSync('users') || []

				// 查找用户（支持用户名或邮箱登录）
				const user = users.find(u => 
					(u.username === this.formData.username || u.email === this.formData.username) &&
					u.password === this.formData.password
				)

				if (!user) {
					uni.showToast({
						title: '用户名或密码错误',
						icon: 'none'
					})
					return
				}

				// 更新最后登录时间
				user.lastLoginAt = new Date().toISOString()
				const userIndex = users.findIndex(u => u.id === user.id)
				if (userIndex !== -1) {
					users[userIndex] = user
					uni.setStorageSync('users', users)
				}

				// 保存当前登录用户信息
				uni.setStorageSync('currentUser', {
					id: user.id,
					username: user.username,
					email: user.email
				})

				// 显示成功提示
				uni.showToast({
					title: '登录成功！',
					icon: 'success',
					duration: 2000
				})

				// 延迟跳转到首页
				setTimeout(() => {
					uni.switchTab({
						url: '/pages/home/index'
					})
				}, 2000)
			},
			goToRegister() {
				uni.navigateTo({
					url: '/pages/auth/register'
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
		padding: 80rpx 40rpx 40rpx;
		width: 100%;
		box-sizing: border-box;
	}

	.header-section {
		text-align: center;
		margin-bottom: 60rpx;
	}

	.main-title {
		display: block;
		font-size: 48rpx;
		font-weight: 300;
		color: #2F5D62;
		margin-bottom: 16rpx;
		letter-spacing: 2rpx;
	}

	.sub-title {
		display: block;
		font-size: 26rpx;
		color: #B0B0B0;
		font-weight: 300;
	}

	.form-card {
		background-color: #FFFFFF;
		border-radius: 24rpx;
		padding: 48rpx 40rpx;
		box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
	}

	.form-group {
		margin-bottom: 40rpx;
	}

	.form-label {
		display: block;
		font-size: 28rpx;
		color: #333;
		margin-bottom: 16rpx;
		font-weight: 400;
	}

	.form-input {
		width: 100%;
		padding: 24rpx !important;
		border: 2rpx solid #E0E0E0;
		border-radius: 12rpx;
		font-size: 28rpx;
		background-color: #FFFFFF;
		color: #333;
		box-sizing: border-box;
		line-height: 1.5;
		-webkit-appearance: none;
		appearance: none;
		min-height: 80rpx;
		display: block;
	}

	.form-input:focus {
		border-color: #2F5D62;
		background-color: #FFFFFF;
		outline: none;
	}

	.submit-btn {
		width: 100%;
		background-color: #2F5D62;
		color: #FFFFFF;
		border: none;
		border-radius: 50rpx;
		padding: 24rpx;
		font-size: 32rpx;
		font-weight: 400;
		box-shadow: 0 4rpx 12rpx rgba(47, 93, 98, 0.2);
		margin-bottom: 32rpx;
	}

	.submit-btn:active {
		opacity: 0.8;
	}

	.submit-btn:disabled {
		background-color: #E0E0E0;
		color: #B0B0B0;
		box-shadow: none;
	}

	.register-link {
		display: flex;
		justify-content: center;
		align-items: center;
		gap: 8rpx;
	}

	.link-text {
		font-size: 26rpx;
		color: #999;
	}

	.link-btn {
		font-size: 26rpx;
		color: #2F5D62;
		font-weight: 500;
	}
</style>

