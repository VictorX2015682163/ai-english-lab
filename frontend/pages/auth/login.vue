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
				<!-- 登录方式切换 -->
				<view class="login-tabs">
					<view 
						class="tab-item" 
						:class="{ active: loginType === 'password' }"
						@click="loginType = 'password'"
					>
						<text>密码登录</text>
					</view>
					<view 
						class="tab-item" 
						:class="{ active: loginType === 'sms' }"
						@click="loginType = 'sms'"
					>
						<text>验证码登录</text>
					</view>
				</view>

				<!-- 密码登录表单 -->
				<view v-if="loginType === 'password'">
				<view class="form-group">
						<text class="form-label">用户名或手机号</text>
						<view class="input-wrapper">
					<input 
						class="form-input" 
						type="text"
						:value="formData.username"
						@input="handleUsernameInput"
								placeholder="请输入用户名或手机号"
								placeholder-class="input-placeholder"
					/>
						</view>
				</view>

				<view class="form-group">
					<text class="form-label">密码</text>
						<view class="input-wrapper">
					<input 
						class="form-input" 
								type="text"
						:value="formData.password"
						@input="handlePasswordInput"
						placeholder="请输入密码"
								placeholder-class="input-placeholder"
						:password="true"
					/>
						</view>
					</view>

					<view class="forgot-password-link">
						<text class="link-btn" @click="goToForgotPassword">忘记密码？</text>
					</view>

					<button class="submit-btn" @click="handleLogin" :disabled="!canSubmitPassword || loading">
						{{ loading ? '登录中...' : '登录' }}
					</button>
				</view>

				<!-- 验证码登录表单 -->
				<view v-if="loginType === 'sms'">
					<view class="form-group">
						<text class="form-label">手机号</text>
						<view class="input-wrapper">
							<input 
								class="form-input" 
								type="number"
								:value="formData.phone"
								@input="handlePhoneInput"
								placeholder="请输入手机号"
								placeholder-class="input-placeholder"
								:maxlength="11"
							/>
						</view>
					</view>

					<view class="form-group">
						<text class="form-label">验证码</text>
						<view class="input-wrapper code-input-wrapper">
							<input 
								class="form-input code-input" 
								type="number"
								:value="formData.smsCode"
								@input="handleSmsCodeInput"
								placeholder="请输入验证码"
								placeholder-class="input-placeholder"
								:maxlength="6"
							/>
							<button 
								class="send-code-btn" 
								:disabled="!canSendCode || sendingCode"
								@click="handleSendCode"
							>
								{{ sendCodeBtnText }}
							</button>
						</view>
					</view>

					<view class="sms-tip">
						<text>未注册的手机号将自动创建账号</text>
					</view>

					<button class="submit-btn" @click="handleSmsLogin" :disabled="!canSubmitSms || loading">
						{{ loading ? '登录中...' : '登录' }}
				</button>
				</view>

				<view class="register-link">
					<text class="link-text">还没有账号？</text>
					<text class="link-btn" @click="goToRegister">立即注册</text>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	import { login, sendSmsCode, smsLogin } from '@/utils/api.js'
	
	export default {
		data() {
			return {
				loading: false,
				sendingCode: false,
				loginType: 'password', // password 或 sms
				countdown: 0,
				formData: {
					username: '',
					password: '',
					phone: '',
					smsCode: ''
				}
			}
		},
		computed: {
			canSubmitPassword() {
				return this.formData.username.length > 0 && this.formData.password.length > 0
			},
			canSubmitSms() {
				return this.formData.phone.length === 11 && this.formData.smsCode.length >= 4
			},
			canSendCode() {
				return this.formData.phone.length === 11 && this.countdown === 0
			},
			sendCodeBtnText() {
				if (this.countdown > 0) {
					return `${this.countdown}秒后重试`
				}
				return this.sendingCode ? '发送中...' : '获取验证码'
			}
		},
		methods: {
			handleUsernameInput(e) {
				this.formData.username = e.detail.value
			},
			handlePasswordInput(e) {
				this.formData.password = e.detail.value
			},
			handlePhoneInput(e) {
				this.formData.phone = e.detail.value
			},
			handleSmsCodeInput(e) {
				this.formData.smsCode = e.detail.value
			},
			startCountdown() {
				this.countdown = 60
				const timer = setInterval(() => {
					this.countdown--
					if (this.countdown <= 0) {
						clearInterval(timer)
					}
				}, 1000)
			},
			async handleSendCode() {
				if (!this.canSendCode) return
				
				// 验证手机号格式
				const phoneRegex = /^1[3-9]\d{9}$/
				if (!phoneRegex.test(this.formData.phone)) {
					uni.showToast({
						title: '请输入有效的手机号',
						icon: 'none'
					})
					return
				}
				
				this.sendingCode = true
				try {
					const response = await sendSmsCode(this.formData.phone, 'login')
					
					// 开发环境显示验证码
					if (response.code) {
						uni.showModal({
							title: '验证码（开发环境）',
							content: `验证码: ${response.code}`,
							showCancel: false
						})
					} else {
						uni.showToast({
							title: '验证码已发送',
							icon: 'success'
						})
					}
					
					this.startCountdown()
				} catch (error) {
					console.error('发送验证码失败:', error)
					uni.showToast({
						title: error.data?.detail || '发送失败，请稍后重试',
						icon: 'none'
					})
				} finally {
					this.sendingCode = false
				}
			},
			async handleLogin() {
				if (!this.canSubmitPassword) {
					uni.showToast({
						title: '请填写完整信息',
						icon: 'none'
					})
					return
				}

				this.loading = true
				try {
					const response = await login(
						this.formData.username,
						this.formData.password
					)
					
					this.handleLoginSuccess(response)
				} catch (error) {
					console.error('登录失败:', error)
					uni.showToast({
						title: error.data?.detail || error.errMsg || '登录失败，请稍后重试',
						icon: 'none',
						duration: 2000
					})
				} finally {
					this.loading = false
				}
			},
			async handleSmsLogin() {
				if (!this.canSubmitSms) {
					uni.showToast({
						title: '请填写完整信息',
						icon: 'none'
					})
					return
				}

				this.loading = true
				try {
					const response = await smsLogin(
						this.formData.phone,
						this.formData.smsCode
					)
					
					this.handleLoginSuccess(response)
				} catch (error) {
					console.error('验证码登录失败:', error)
					uni.showToast({
						title: error.data?.detail || error.errMsg || '登录失败，请稍后重试',
						icon: 'none',
						duration: 2000
					})
				} finally {
					this.loading = false
				}
			},
			handleLoginSuccess(response) {
				// 保存token和用户信息
				uni.setStorageSync('token', response.access_token)
				uni.setStorageSync('currentUser', {
					id: response.user.id,
					username: response.user.username,
					email: response.user.email,
					phone: response.user.phone
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
			},
			goToForgotPassword() {
				uni.navigateTo({
					url: '/pages/auth/forgot-password'
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

	/* 登录方式切换标签 */
	.login-tabs {
		display: flex;
		margin-bottom: 40rpx;
		border-bottom: 2rpx solid #E0E0E0;
	}

	.tab-item {
		flex: 1;
		text-align: center;
		padding: 20rpx 0;
		color: #999;
		font-size: 28rpx;
		position: relative;
	}

	.tab-item.active {
		color: #2F5D62;
		font-weight: 500;
	}

	.tab-item.active::after {
		content: '';
		position: absolute;
		bottom: -2rpx;
		left: 50%;
		transform: translateX(-50%);
		width: 60rpx;
		height: 4rpx;
		background-color: #2F5D62;
		border-radius: 2rpx;
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

	.input-wrapper {
		width: 100%;
		height: 88rpx;
		padding: 0 24rpx;
		border: 2rpx solid #E0E0E0;
		border-radius: 12rpx;
		background-color: #FFFFFF;
		display: flex;
		align-items: center;
	}

	.code-input-wrapper {
		padding-right: 12rpx;
	}

	.form-input {
		flex: 1;
		height: 100%;
		font-size: 28rpx;
		color: #333;
		background-color: transparent;
		border: none;
		outline: none;
	}

	.code-input {
		flex: 1;
	}

	.send-code-btn {
		width: 180rpx;
		height: 64rpx;
		line-height: 64rpx;
		font-size: 24rpx;
		background-color: #2F5D62;
		color: #FFFFFF;
		border: none;
		border-radius: 8rpx;
		padding: 0;
		margin: 0;
	}

	.send-code-btn:disabled {
		background-color: #E0E0E0;
		color: #999;
	}

	.input-placeholder {
		color: #B0B0B0;
		font-size: 28rpx;
	}

	.sms-tip {
		margin-bottom: 32rpx;
		text-align: center;
	}

	.sms-tip text {
		font-size: 24rpx;
		color: #999;
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

	.forgot-password-link {
		display: flex;
		justify-content: flex-end;
		margin-bottom: 32rpx;
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
