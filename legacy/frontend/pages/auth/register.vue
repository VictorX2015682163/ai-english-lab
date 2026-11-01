<template>
	<view class="container">
		<view class="content">
			<!-- 顶部标题 -->
			<view class="header-section">
				<text class="main-title">创建账号</text>
				<text class="sub-title">开始你的英语学习之旅</text>
			</view>

			<!-- 注册表单 -->
			<view class="form-card">
				<view class="form-group">
					<text class="form-label">用户名</text>
					<input 
						class="form-input" 
						type="text"
						v-model="formData.username"
						placeholder="请输入用户名（3-20个字符）"
						placeholder-style="color: #B0B0B0"
						:maxlength="20"
						:disabled="false"
						:readonly="false"
					/>
				</view>

				<view class="form-group">
					<text class="form-label">邮箱</text>
					<input 
						class="form-input" 
						type="text"
						v-model="formData.email"
						placeholder="请输入邮箱地址"
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
						placeholder="请输入密码（至少6个字符）"
						placeholder-style="color: #B0B0B0"
						:password="true"
						:disabled="false"
						:readonly="false"
					/>
				</view>

				<view class="form-group">
					<text class="form-label">确认密码</text>
					<input 
						class="form-input" 
						type="password"
						v-model="formData.confirmPassword"
						placeholder="请再次输入密码"
						placeholder-style="color: #B0B0B0"
						:password="true"
						:disabled="false"
						:readonly="false"
					/>
				</view>

				<view class="form-tip">
					<text>注册即表示同意我们的服务条款和隐私政策</text>
				</view>

				<button class="submit-btn" @click="handleRegister" :class="{ disabled: !canSubmit }">
					创建账号
				</button>

				<view class="login-link">
					<text class="link-text">已有账号？</text>
					<text class="link-btn" @click="goToLogin">立即登录</text>
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
					email: '',
					password: '',
					confirmPassword: ''
				}
			}
		},
		computed: {
			canSubmit() {
				const usernameValid = this.formData.username && this.formData.username.trim().length >= 3
				const emailValid = this.formData.email && this.formData.email.trim().length > 0
				const passwordValid = this.formData.password && this.formData.password.length >= 6
				const confirmValid = this.formData.password === this.formData.confirmPassword
				return usernameValid && emailValid && passwordValid && confirmValid
			}
		},
		methods: {
			validateForm() {
				// 验证用户名
				if (!this.formData.username || this.formData.username.trim().length < 3 || this.formData.username.trim().length > 20) {
					uni.showToast({
						title: '用户名长度应在3-20个字符之间',
						icon: 'none',
						duration: 2000
					})
					return false
				}

				// 验证邮箱格式
				if (!this.formData.email || this.formData.email.trim().length === 0) {
					uni.showToast({
						title: '请输入邮箱地址',
						icon: 'none',
						duration: 2000
					})
					return false
				}
				
				const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
				if (!emailRegex.test(this.formData.email.trim())) {
					uni.showToast({
						title: '请输入有效的邮箱地址',
						icon: 'none',
						duration: 2000
					})
					return false
				}

				// 验证密码
				if (!this.formData.password || this.formData.password.length < 6) {
					uni.showToast({
						title: '密码长度至少为6个字符',
						icon: 'none',
						duration: 2000
					})
					return false
				}

				// 验证确认密码
				if (this.formData.password !== this.formData.confirmPassword) {
					uni.showToast({
						title: '两次输入的密码不一致',
						icon: 'none',
						duration: 2000
					})
					return false
				}

				return true
			},
			checkUsernameExists(username) {
				// 检查用户名是否已存在
				const users = uni.getStorageSync('users') || []
				return users.some(user => user.username === username)
			},
			checkEmailExists(email) {
				// 检查邮箱是否已存在
				const users = uni.getStorageSync('users') || []
				return users.some(user => user.email === email)
			},
			handleRegister() {
				// 先验证表单
				if (!this.validateForm()) {
					return
				}

				// 检查用户名是否已存在
				if (this.checkUsernameExists(this.formData.username.trim())) {
					uni.showToast({
						title: '该用户名已被使用',
						icon: 'none',
						duration: 2000
					})
					return
				}

				// 检查邮箱是否已存在
				if (this.checkEmailExists(this.formData.email.trim())) {
					uni.showToast({
						title: '该邮箱已被注册',
						icon: 'none',
						duration: 2000
					})
					return
				}

				// 创建用户账号
				const users = uni.getStorageSync('users') || []
				const newUser = {
					id: Date.now().toString(),
					username: this.formData.username.trim(),
					email: this.formData.email.trim(),
					password: this.formData.password, // 实际项目中应该加密
					createdAt: new Date().toISOString(),
					lastLoginAt: null
				}

				users.push(newUser)
				uni.setStorageSync('users', users)

				// 保存当前登录用户信息
				uni.setStorageSync('currentUser', {
					id: newUser.id,
					username: newUser.username,
					email: newUser.email
				})

				// 显示成功提示
				uni.showToast({
					title: '注册成功！',
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

	.form-tip {
		margin-bottom: 40rpx;
		text-align: center;
	}

	.form-tip text {
		font-size: 24rpx;
		color: #999;
		line-height: 1.6;
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

	.submit-btn.disabled {
		background-color: #E0E0E0;
		color: #B0B0B0;
		box-shadow: none;
		opacity: 0.6;
	}
	
	.submit-btn.disabled:active {
		opacity: 0.6;
	}

	.login-link {
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

