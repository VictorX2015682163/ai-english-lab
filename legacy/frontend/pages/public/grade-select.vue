<template>
	<view class="container">
		<scroll-view class="content" scroll-y>
			<!-- 顶部标题 -->
			<view class="header-section">
				<text class="main-title">公立学校模式：从年级开始</text>
				<text class="sub-title">告诉 AI 你几年级了，我们按教材帮你出题</text>
			</view>

			<!-- 步骤条 -->
			<view class="steps-bar">
				<view class="step-item active">
					<text class="step-number">1</text>
					<text class="step-text">选择年级与教材</text>
				</view>
				<view class="step-divider"></view>
				<view class="step-item">
					<text class="step-number">2</text>
					<text class="step-text">开始练习</text>
				</view>
			</view>

			<!-- 选择区 -->
			<view class="select-section">
				<!-- 年级选择 -->
				<view class="form-group">
					<text class="form-label">选择年级</text>
					<view class="grade-buttons">
						<view 
							v-for="(grade, index) in grades" 
							:key="index"
							class="grade-btn"
							:class="{ active: selectedGrade === grade }"
							@click="selectGrade(grade)"
						>
							<text>{{ grade }}</text>
						</view>
					</view>
				</view>

				<!-- 教材版本选择 -->
				<view class="form-group">
					<text class="form-label">教材版本</text>
					<picker 
						mode="selector" 
						:range="textbookVersions" 
						:value="selectedVersionIndex"
						@change="onVersionChange"
					>
						<view class="picker-view">
							<text>{{ textbookVersions[selectedVersionIndex] || '请选择教材版本' }}</text>
							<text class="picker-arrow">›</text>
						</view>
					</picker>
				</view>

				<!-- 单元选择 -->
				<view class="form-group">
					<text class="form-label">选择单元</text>
					<picker 
						mode="selector" 
						:range="units" 
						:value="selectedUnitIndex"
						@change="onUnitChange"
					>
						<view class="picker-view">
							<text>{{ units[selectedUnitIndex] || '请选择单元' }}</text>
							<text class="picker-arrow">›</text>
						</view>
					</picker>
				</view>

				<view class="form-tip">
					<text>如果不确定教材版本，可以先选默认版本，后续随时调整。</text>
				</view>
			</view>

			<!-- 开始练习按钮区 -->
			<view class="action-section">
				<button 
					class="start-btn" 
					:class="{ disabled: !canStart }"
					:disabled="!canStart"
					@click="startPractice"
				>
					开始出题
				</button>
				<text class="action-tip">系统会根据你选择的年级和单元，生成基础词汇与语法练习。</text>
			</view>
		</scroll-view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				selectedGrade: '',
				grades: ['三年级', '四年级', '五年级', '六年级', '初一', '初二', '初三'],
				textbookVersions: ['人教版', '北师大版', '外研版', '苏教版'],
				selectedVersionIndex: 0,
				units: ['Unit 1', 'Unit 2', 'Unit 3', 'Unit 4', 'Unit 5', 'Unit 6'],
				selectedUnitIndex: -1
			}
		},
		computed: {
			canStart() {
				return this.selectedGrade && this.selectedVersionIndex >= 0 && this.selectedUnitIndex >= 0
			}
		},
		methods: {
			selectGrade(grade) {
				this.selectedGrade = grade
			},
			onVersionChange(e) {
				this.selectedVersionIndex = e.detail.value
			},
			onUnitChange(e) {
				this.selectedUnitIndex = e.detail.value
			},
			startPractice() {
				if (!this.canStart) return
				
				// 保存选择信息到本地存储
				const practiceInfo = {
					grade: this.selectedGrade,
					version: this.textbookVersions[this.selectedVersionIndex],
					unit: this.units[this.selectedUnitIndex]
				}
				uni.setStorageSync('practiceInfo', practiceInfo)
				
				// 跳转到练习页
				uni.navigateTo({
					url: '/pages/public/practice'
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

	.steps-bar {
		display: flex;
		align-items: center;
		justify-content: center;
		margin-bottom: 60rpx;
		padding: 0 40rpx;
	}

	.step-item {
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.step-number {
		width: 60rpx;
		height: 60rpx;
		border-radius: 50%;
		background-color: #E0E0E0;
		color: #999;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 28rpx;
		margin-bottom: 12rpx;
	}

	.step-item.active .step-number {
		background-color: #2F5D62;
		color: #FFFFFF;
	}

	.step-text {
		font-size: 24rpx;
		color: #999;
	}

	.step-item.active .step-text {
		color: #2F5D62;
	}

	.step-divider {
		width: 120rpx;
		height: 2rpx;
		background-color: #E0E0E0;
		margin: 0 20rpx;
		margin-bottom: 30rpx;
	}

	.select-section {
		background-color: #FFFFFF;
		border-radius: 24rpx;
		padding: 48rpx 40rpx;
		margin-bottom: 40rpx;
		box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
	}

	.form-group {
		margin-bottom: 48rpx;
	}

	.form-label {
		display: block;
		font-size: 28rpx;
		color: #2F5D62;
		margin-bottom: 24rpx;
		font-weight: 400;
	}

	.grade-buttons {
		display: flex;
		flex-wrap: wrap;
		gap: 20rpx;
	}

	.grade-btn {
		padding: 16rpx 32rpx;
		border-radius: 50rpx;
		border: 2rpx solid #E0E0E0;
		background-color: #FFFFFF;
		font-size: 26rpx;
		color: #666;
		transition: all 0.3s ease;
	}

	.grade-btn.active {
		background-color: #2F5D62;
		color: #FFFFFF;
		border-color: #2F5D62;
		transform: scale(1.05);
	}

	.picker-view {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 24rpx 32rpx;
		background-color: #FAFAFA;
		border-radius: 12rpx;
		border: 1rpx solid #E0E0E0;
		font-size: 28rpx;
		color: #333;
	}

	.picker-arrow {
		font-size: 36rpx;
		color: #B0B0B0;
	}

	.form-tip {
		margin-top: 40rpx;
		padding-top: 32rpx;
		border-top: 1rpx solid #F0F0F0;
	}

	.form-tip text {
		font-size: 24rpx;
		color: #999;
		line-height: 1.6;
	}

	.action-section {
		display: flex;
		flex-direction: column;
		align-items: center;
		padding: 40rpx 0;
	}

	.start-btn {
		background-color: #2F5D62;
		color: #FFFFFF;
		border: none;
		border-radius: 50rpx;
		padding: 24rpx 80rpx;
		font-size: 32rpx;
		font-weight: 400;
		margin-bottom: 24rpx;
		box-shadow: 0 4rpx 12rpx rgba(47, 93, 98, 0.2);
	}

	.start-btn.disabled {
		background-color: #E0E0E0;
		color: #B0B0B0;
		box-shadow: none;
	}

	.action-tip {
		font-size: 24rpx;
		color: #999;
		text-align: center;
		line-height: 1.6;
	}
</style>

