<template>
	<view class="container">
		<scroll-view class="content" scroll-y>
			<!-- 头部区域 -->
			<view class="header-section">
				<text class="main-title">我的</text>
			</view>

			<!-- 头像和基本信息 -->
			<view class="profile-section">
				<view class="avatar-wrapper" @click="changeAvatar">
					<image 
						v-if="profile.avatar" 
						:src="getAvatarUrl(profile.avatar)" 
						class="avatar"
						mode="aspectFill"
					/>
					<view v-else class="avatar-placeholder">
						<text class="avatar-text">{{ profile.nickname || profile.username || '我' }}</text>
					</view>
					<view class="avatar-edit-icon">📷</view>
				</view>
				<text class="username">{{ profile.nickname || profile.username || '未设置昵称' }}</text>
				<text class="phone">{{ profile.phone || '' }}</text>
			</view>

			<!-- 编辑表单 -->
			<view class="form-card">
				<view class="form-group">
					<text class="form-label">昵称</text>
					<view class="input-wrapper">
						<input
							class="form-input"
							type="text"
							:value="formData.nickname"
							@input="handleNicknameInput"
							placeholder="请输入昵称"
							placeholder-class="input-placeholder"
							:maxlength="50"
						/>
					</view>
				</view>

				<view class="form-group">
					<text class="form-label">个人简介</text>
					<view class="input-wrapper">
						<textarea
							class="form-textarea"
							:value="formData.bio"
							@input="handleBioInput"
							placeholder="介绍一下自己吧"
							placeholder-class="input-placeholder"
							:maxlength="500"
							auto-height
						/>
					</view>
				</view>

				<view class="form-group">
					<text class="form-label">性别</text>
					<view class="radio-group">
						<view 
							class="radio-item"
							:class="{ active: formData.gender === 'male' }"
							@click="formData.gender = 'male'"
						>
							<text>男</text>
						</view>
						<view 
							class="radio-item"
							:class="{ active: formData.gender === 'female' }"
							@click="formData.gender = 'female'"
						>
							<text>女</text>
						</view>
						<view 
							class="radio-item"
							:class="{ active: formData.gender === 'other' }"
							@click="formData.gender = 'other'"
						>
							<text>其他</text>
						</view>
					</view>
				</view>

				<view class="form-group">
					<text class="form-label">邮箱</text>
					<view class="input-wrapper">
						<input
							class="form-input"
							type="text"
							:value="formData.email"
							@input="handleEmailInput"
							placeholder="请输入邮箱（可选）"
							placeholder-class="input-placeholder"
						/>
					</view>
				</view>

				<button class="submit-btn" @click="handleSave" :disabled="loading">
					{{ loading ? '保存中...' : '保存资料' }}
				</button>
			</view>

			<!-- 其他信息 -->
			<view class="info-card">
				<view class="info-item">
					<text class="info-label">用户名</text>
					<text class="info-value">{{ profile.username }}</text>
				</view>
				<view class="info-item">
					<text class="info-label">注册时间</text>
					<text class="info-value">{{ formatDate(profile.created_at) }}</text>
				</view>
			</view>
		</scroll-view>
	</view>
</template>

<script>
import { getProfile, updateProfile, uploadAvatar } from '@/utils/api.js'

export default {
	data() {
		return {
			loading: false,
			profile: {
				id: null,
				username: '',
				phone: '',
				email: null,
				avatar: null,
				nickname: null,
				bio: null,
				gender: null,
				birthday: null,
				created_at: null
			},
			formData: {
				nickname: '',
				bio: '',
				gender: null,
				email: ''
			}
		}
	},
	onLoad() {
		this.loadProfile()
	},
	onShow() {
		this.loadProfile()
	},
	methods: {
		async loadProfile() {
			const token = uni.getStorageSync('token')
			if (!token) {
				uni.showToast({
					title: '请先登录',
					icon: 'none'
				})
				setTimeout(() => {
					uni.navigateTo({
						url: '/pages/auth/login'
					})
				}, 1500)
				return
			}

			try {
				const response = await getProfile()
				this.profile = response
				this.formData = {
					nickname: response.nickname || '',
					bio: response.bio || '',
					gender: response.gender || null,
					email: response.email || ''
				}
			} catch (error) {
				console.error('加载用户资料失败:', error)
				if (error.statusCode === 401) {
					uni.showToast({
						title: '登录已过期，请重新登录',
						icon: 'none'
					})
					setTimeout(() => {
						uni.navigateTo({
							url: '/pages/auth/login'
						})
					}, 1500)
				} else {
					uni.showToast({
						title: error.data?.detail || error.errMsg || '加载失败',
						icon: 'none'
					})
				}
			}
		},
		handleNicknameInput(e) {
			this.formData.nickname = e.detail.value
		},
		handleBioInput(e) {
			this.formData.bio = e.detail.value
		},
		handleEmailInput(e) {
			this.formData.email = e.detail.value
		},
		async handleSave() {
			this.loading = true
			try {
				const updateData = {}
				if (this.formData.nickname !== (this.profile.nickname || '')) {
					updateData.nickname = this.formData.nickname || null
				}
				if (this.formData.bio !== (this.profile.bio || '')) {
					updateData.bio = this.formData.bio || null
				}
				if (this.formData.gender !== this.profile.gender) {
					updateData.gender = this.formData.gender
				}
				if (this.formData.email !== (this.profile.email || '')) {
					updateData.email = this.formData.email || null
				}

				if (Object.keys(updateData).length === 0) {
					uni.showToast({
						title: '没有需要保存的内容',
						icon: 'none'
					})
					this.loading = false
					return
				}

				const response = await updateProfile(updateData)
				this.profile = response
				uni.showToast({
					title: '保存成功',
					icon: 'success'
				})
			} catch (error) {
				console.error('保存失败:', error)
				uni.showToast({
					title: error.data?.detail || error.errMsg || '保存失败',
					icon: 'none'
				})
			} finally {
				this.loading = false
			}
		},
		changeAvatar() {
			uni.chooseImage({
				count: 1,
				sizeType: ['compressed'],
				sourceType: ['album', 'camera'],
				success: (res) => {
					const tempFilePath = res.tempFilePaths[0]
					this.uploadAvatarFile(tempFilePath)
				}
			})
		},
		async uploadAvatarFile(filePath) {
			uni.showLoading({
				title: '上传中...'
			})

			try {
				const response = await uploadAvatar(filePath)
				if (response.avatar_url) {
					this.profile.avatar = response.avatar_url
				}
				uni.hideLoading()
				uni.showToast({
					title: '头像上传成功',
					icon: 'success'
				})
				// 重新加载资料
				this.loadProfile()
			} catch (error) {
				uni.hideLoading()
				console.error('上传头像失败:', error)
				uni.showToast({
					title: error.data?.detail || error.errMsg || '上传失败',
					icon: 'none'
				})
			}
		},
		getAvatarUrl(avatar) {
			if (!avatar) return ''
			if (avatar.startsWith('http')) {
				return avatar
			}
			// 如果是相对路径，拼接API地址
			return `http://127.0.0.1:8000${avatar}`
		},
		formatDate(dateStr) {
			if (!dateStr) return ''
			const date = new Date(dateStr)
			return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
		}
	}
}
</script>

<style>
.container {
	min-height: 100vh;
	background-color: #F8F6F2;
}

.content {
	height: calc(100vh - 88rpx);
}

.header-section {
	padding: 60rpx 40rpx 40rpx;
	text-align: center;
}

.main-title {
	font-size: 48rpx;
	font-weight: 600;
	color: #2F5D62;
}

.profile-section {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 40rpx 0 60rpx;
}

.avatar-wrapper {
	position: relative;
	width: 160rpx;
	height: 160rpx;
	border-radius: 50%;
	overflow: hidden;
	margin-bottom: 20rpx;
}

.avatar {
	width: 100%;
	height: 100%;
}

.avatar-placeholder {
	width: 100%;
	height: 100%;
	background-color: #2F5D62;
	display: flex;
	align-items: center;
	justify-content: center;
}

.avatar-text {
	color: #FFFFFF;
	font-size: 48rpx;
	font-weight: 500;
}

.avatar-edit-icon {
	position: absolute;
	bottom: 0;
	right: 0;
	background-color: rgba(0, 0, 0, 0.6);
	width: 50rpx;
	height: 50rpx;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 28rpx;
}

.username {
	font-size: 36rpx;
	font-weight: 500;
	color: #2F5D62;
	margin-bottom: 10rpx;
}

.phone {
	font-size: 28rpx;
	color: #999;
}

.form-card {
	background-color: #FFFFFF;
	margin: 0 30rpx 30rpx;
	padding: 40rpx;
	border-radius: 20rpx;
	box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.form-group {
	margin-bottom: 40rpx;
}

.form-label {
	display: block;
	font-size: 28rpx;
	color: #333;
	margin-bottom: 20rpx;
	font-weight: 500;
}

.input-wrapper {
	background-color: #F5F5F5;
	border-radius: 10rpx;
	padding: 20rpx;
}

.form-input {
	font-size: 28rpx;
	color: #333;
	width: 100%;
}

.form-textarea {
	font-size: 28rpx;
	color: #333;
	width: 100%;
	min-height: 120rpx;
}

.input-placeholder {
	color: #999;
}

.radio-group {
	display: flex;
	gap: 20rpx;
}

.radio-item {
	flex: 1;
	padding: 20rpx;
	text-align: center;
	border-radius: 10rpx;
	background-color: #F5F5F5;
	color: #666;
	font-size: 28rpx;
}

.radio-item.active {
	background-color: #2F5D62;
	color: #FFFFFF;
}

.submit-btn {
	width: 100%;
	background-color: #2F5D62;
	color: #FFFFFF;
	font-size: 32rpx;
	padding: 24rpx 0;
	border-radius: 10rpx;
	margin-top: 40rpx;
}

.submit-btn:disabled {
	background-color: #CCC;
}

.info-card {
	background-color: #FFFFFF;
	margin: 0 30rpx 30rpx;
	padding: 40rpx;
	border-radius: 20rpx;
	box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.info-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20rpx 0;
	border-bottom: 1rpx solid #F0F0F0;
}

.info-item:last-child {
	border-bottom: none;
}

.info-label {
	font-size: 28rpx;
	color: #666;
}

.info-value {
	font-size: 28rpx;
	color: #333;
}
</style>

