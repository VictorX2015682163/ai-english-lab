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
					<view class="input-wrapper">
					<input 
						class="form-input" 
						type="text"
						:value="formData.username"
						@input="handleUsernameInput"
						placeholder="请输入用户名（3-20个字符）"
							placeholder-class="input-placeholder"
						:maxlength="20"
					/>
					</view>
				</view>

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
					<text class="form-label">密码</text>
					<view class="input-wrapper">
					<input 
						class="form-input" 
							type="text"
						:value="formData.password"
						@input="handlePasswordInput"
						placeholder="请输入密码（至少6个字符）"
							placeholder-class="input-placeholder"
						:password="true"
					/>
					</view>
				</view>

				<view class="form-group">
					<text class="form-label">确认密码</text>
					<view class="input-wrapper">
					<input 
						class="form-input" 
							type="text"
						:value="formData.confirmPassword"
						@input="handleConfirmPasswordInput"
						placeholder="请再次输入密码"
							placeholder-class="input-placeholder"
						:password="true"
					/>
					</view>
				</view>

				<view class="form-tip">
					<text>注册即表示同意我们的服务条款和隐私政策</text>
				</view>

				<button 
					class="submit-btn" 
					@click="handleRegister" 
					:disabled="!canSubmit || loading"
					:class="{ 'btn-disabled': !canSubmit || loading }"
				>
					{{ loading ? '注册中...' : '创建账号' }}
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
	import { register } from '@/utils/api.js'
	
	export default {
		data() {
			return {
				loading: false,
				formData: {
					username: '',
					phone: '',
					password: '',
					confirmPassword: ''
				}
			}
		},
		computed: {
			canSubmit() {
				const result = this.formData.username.length >= 3 &&
				       this.formData.phone.length === 11 &&
				       this.formData.password.length >= 6 &&
				       this.formData.password === this.formData.confirmPassword
				console.log('canSubmit:', result, {
					username: this.formData.username.length,
					phone: this.formData.phone.length,
					password: this.formData.password.length,
					confirmMatch: this.formData.password === this.formData.confirmPassword
				})
				return result
			}
		},
		methods: {
			handleUsernameInput(e) {
				console.log('用户名输入:', e.detail.value)
				this.formData.username = e.detail.value
			},
			handlePhoneInput(e) {
				console.log('手机号输入:', e.detail.value)
				this.formData.phone = e.detail.value
			},
			handlePasswordInput(e) {
				console.log('密码输入:', e.detail.value)
				this.formData.password = e.detail.value
			},
			handleConfirmPasswordInput(e) {
				console.log('确认密码输入:', e.detail.value)
				this.formData.confirmPassword = e.detail.value
			},
			validateForm() {
				// 验证用户名
				if (this.formData.username.length < 3 || this.formData.username.length > 20) {
					uni.showToast({
						title: '用户名长度应在3-20个字符之间',
						icon: 'none'
					})
					return false
				}

				// 验证手机号格式
				const phoneRegex = /^1[3-9]\d{9}$/
				if (!phoneRegex.test(this.formData.phone)) {
					uni.showToast({
						title: '请输入有效的手机号',
						icon: 'none'
					})
					return false
				}

				// 验证密码
				if (this.formData.password.length < 6) {
					uni.showToast({
						title: '密码长度至少为6个字符',
						icon: 'none'
					})
					return false
				}

				// 验证确认密码
				if (this.formData.password !== this.formData.confirmPassword) {
					uni.showToast({
						title: '两次输入的密码不一致',
						icon: 'none'
					})
					return false
				}

				return true
			},
			async handleRegister() {
				console.log('点击注册按钮')
				console.log('表单数据:', this.formData)
				console.log('canSubmit:', this.canSubmit)
				
				if (!this.validateForm()) {
					console.log('表单验证失败')
					return
				}

				console.log('开始注册请求')
				this.loading = true
				try {
					const response = await register(
						this.formData.username,
						this.formData.phone,
						this.formData.password
					)
					console.log('注册成功:', response)
					
					// 保存token和用户信息
					uni.setStorageSync('token', response.access_token)
				uni.setStorageSync('currentUser', {
						id: response.user.id,
						username: response.user.username,
						phone: response.user.phone
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
				} catch (error) {
					console.error('注册失败:', error)
					let errorMsg = '注册失败，请稍后重试'
					if (error && error.data && error.data.detail) {
						errorMsg = String(error.data.detail)
					} else if (error && error.errMsg) {
						errorMsg = String(error.errMsg)
					}
					uni.showToast({
						title: errorMsg,
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

	.form-input {
		flex: 1;
		height: 100%;
		font-size: 28rpx;
		color: #333;
		background-color: transparent;
		border: none;
		outline: none;
	}

	.input-placeholder {
		color: #B0B0B0;
		font-size: 28rpx;
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

	.submit-btn:disabled,
	.submit-btn.btn-disabled {
		background-color: #E0E0E0;
		color: #B0B0B0;
		box-shadow: none;
		pointer-events: none;
	}
	
	.submit-btn {
		position: relative;
		z-index: 1;
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
