<template>
	<view class="container">
		<view class="content">
			<!-- 顶部标题 -->
			<view class="header-section">
				<text class="main-title">忘记密码</text>
				<text class="sub-title">请输入您的邮箱地址</text>
			</view>

			<!-- 表单卡片 -->
			<view class="form-card" v-if="!showResetForm">
				<view class="form-group">
					<text class="form-label">邮箱</text>
					<input 
						class="form-input" 
						type="text"
						:value="formData.email"
						@input="handleEmailInput"
						placeholder="请输入注册时的邮箱地址"
						placeholder-style="color: #B0B0B0"
					/>
				</view>

				<button class="submit-btn" @click="handleForgotPassword" :disabled="!canSubmit || loading">
					{{ loading ? '发送中...' : '发送重置链接' }}
				</button>

				<view class="login-link">
					<text class="link-text">想起密码了？</text>
					<text class="link-btn" @click="goToLogin">返回登录</text>
				</view>
			</view>

			<!-- 重置密码表单 -->
			<view class="form-card" v-if="showResetForm">
				<view class="form-group">
					<text class="form-label">重置Token</text>
					<input 
						class="form-input" 
						type="text"
						:value="formData.token"
						@input="handleTokenInput"
						placeholder="请输入收到的重置token"
						placeholder-style="color: #B0B0B0"
					/>
				</view>

				<view class="form-group">
					<text class="form-label">新密码</text>
					<input 
						class="form-input" 
						type="password"
						:value="formData.newPassword"
						@input="handleNewPasswordInput"
						placeholder="请输入新密码（至少6个字符）"
						placeholder-style="color: #B0B0B0"
						password
					/>
				</view>

				<view class="form-group">
					<text class="form-label">确认新密码</text>
					<input 
						class="form-input" 
						type="password"
						:value="formData.confirmPassword"
						@input="handleConfirmPasswordInput"
						placeholder="请再次输入新密码"
						placeholder-style="color: #B0B0B0"
						password
					/>
				</view>

				<button class="submit-btn" @click="handleResetPassword" :disabled="!canResetSubmit || loading">
					{{ loading ? '重置中...' : '重置密码' }}
				</button>

				<view class="login-link">
					<text class="link-text">想起密码了？</text>
					<text class="link-btn" @click="goToLogin">返回登录</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	import { forgotPassword, resetPassword } from '@/utils/api.js'
	
	export default {
		data() {
			return {
				loading: false,
				showResetForm: false,
				formData: {
					email: '',
					token: '',
					newPassword: '',
					confirmPassword: ''
				}
			}
		},
		computed: {
			canSubmit() {
				return this.formData.email.length > 0
			},
			canResetSubmit() {
				return this.formData.token.length > 0 &&
				       this.formData.newPassword.length >= 6 &&
				       this.formData.newPassword === this.formData.confirmPassword
			}
		},
		methods: {
			handleEmailInput(e) {
				this.formData.email = e.detail.value
			},
			handleTokenInput(e) {
				this.formData.token = e.detail.value
			},
			handleNewPasswordInput(e) {
				this.formData.newPassword = e.detail.value
			},
			handleConfirmPasswordInput(e) {
				this.formData.confirmPassword = e.detail.value
			},
			async handleForgotPassword() {
				if (!this.canSubmit) {
					uni.showToast({
						title: '请输入邮箱地址',
						icon: 'none'
					})
					return
				}

				// 验证邮箱格式
				const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
				if (!emailRegex.test(this.formData.email)) {
					uni.showToast({
						title: '请输入有效的邮箱地址',
						icon: 'none'
					})
					return
				}

				this.loading = true
				try {
					const response = await forgotPassword(this.formData.email)
					uni.showToast({
						title: '重置token已生成，请查看返回信息',
						icon: 'none',
						duration: 3000
					})
					
					// 从返回消息中提取token（开发环境）
					// 生产环境应该通过邮件发送，这里简化处理
					const tokenMatch = response.message.match(/token已生成.*?:\s*([^\s]+)/)
					if (tokenMatch) {
						this.formData.token = tokenMatch[1]
					}
					
					// 显示重置密码表单
					this.showResetForm = true
				} catch (error) {
					console.error('忘记密码请求失败:', error)
					uni.showToast({
						title: error.data?.detail || error.errMsg || '请求失败，请稍后重试',
						icon: 'none',
						duration: 2000
					})
				} finally {
					this.loading = false
				}
			},
			async handleResetPassword() {
				if (!this.canResetSubmit) {
					uni.showToast({
						title: '请填写完整信息',
						icon: 'none'
					})
					return
				}

				if (this.formData.newPassword !== this.formData.confirmPassword) {
					uni.showToast({
						title: '两次输入的密码不一致',
						icon: 'none'
					})
					return
				}

				this.loading = true
				try {
					await resetPassword(this.formData.token, this.formData.newPassword)
					uni.showToast({
						title: '密码重置成功！',
						icon: 'success',
						duration: 2000
					})
					
					// 延迟跳转到登录页
					setTimeout(() => {
						uni.navigateTo({
							url: '/pages/auth/login'
						})
					}, 2000)
				} catch (error) {
					console.error('重置密码失败:', error)
					uni.showToast({
						title: error.data?.detail || error.errMsg || '重置失败，请稍后重试',
						icon: 'none',
						duration: 2000
					})
				} finally {
					this.loading = false
				}
			},
			goToLogin() {
				uni.navigateTo({
					url: '/pages/auth/login'
				})
			}
		}
	}
</script>

<style>
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
		height: 88rpx;
		padding: 0 24rpx;
		border: 2rpx solid #E0E0E0;
		border-radius: 12rpx;
		font-size: 28rpx;
		background-color: #FFFFFF;
		color: #333;
		box-sizing: border-box;
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

