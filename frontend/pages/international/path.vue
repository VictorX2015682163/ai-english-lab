<template>
	<view class="container">
		<scroll-view class="content" scroll-y>
			<!-- 提示条（如果未完成测试） -->
			<view class="tip-banner" v-if="!testCompleted">
				<text class="tip-text">建议先完成分级测试，以便更精准推荐</text>
				<button class="tip-btn" @click="goToTest">去测试</button>
			</view>

			<!-- 顶部标题 -->
			<view class="header-section">
				<text class="main-title">你的国际学校学习路径</text>
				<text class="sub-title">基于分级测试，由 AI 推荐学习模块</text>
			</view>

			<!-- 学习路径模块区 -->
			<view class="path-section">
				<view class="path-header">
					<text class="current-level">当前水平：{{ currentLevel }}</text>
					<view class="target-selector">
						<text class="target-label">目标：</text>
						<picker 
							mode="selector" 
							:range="targets" 
							:value="selectedTargetIndex"
							@change="onTargetChange"
						>
							<view class="target-picker">
								<text>{{ targets[selectedTargetIndex] || '请选择目标' }}</text>
								<text class="picker-arrow">›</text>
							</view>
						</picker>
					</view>
				</view>

				<view class="modules-grid">
					<view 
						v-for="(module, index) in learningModules" 
						:key="index"
						class="module-card"
						:class="{ added: module.added }"
					>
						<view class="module-header">
							<text class="module-name">{{ module.name }}</text>
							<text class="module-tag" :class="module.tagType">{{ module.tag }}</text>
						</view>
						<text class="module-desc">{{ module.description }}</text>
						<button 
							class="module-btn"
							:class="{ added: module.added }"
							@click="toggleModule(index)"
						>
							{{ module.added ? '已加入计划' : '加入计划' }}
						</button>
					</view>
				</view>
			</view>

			<!-- AI 学习教练对话区 -->
			<view class="coach-section">
				<text class="coach-title">AI Learning Coach</text>
				
				<scroll-view class="chat-messages" scroll-y :scroll-top="scrollTop" scroll-with-animation>
					<view 
						v-for="(message, index) in chatMessages" 
						:key="index"
						class="message-item"
						:class="message.type"
					>
						<text class="message-text">{{ message.text }}</text>
					</view>
				</scroll-view>

				<view class="chat-input-area">
					<view class="quick-prompts">
						<button 
							v-for="(prompt, index) in quickPrompts" 
							:key="index"
							class="prompt-btn"
							@click="sendQuickPrompt(prompt)"
						>
							{{ prompt }}
						</button>
					</view>
					<view class="input-row">
						<input 
							class="chat-input" 
							v-model="inputText" 
							placeholder="输入你的问题..."
							placeholder-style="color: #B0B0B0"
							@confirm="sendMessage"
						/>
						<button class="send-btn" @click="sendMessage">发送</button>
					</view>
				</view>
			</view>
		</scroll-view>
	</view>
</template>

<script>
	import { getLearningModules, toggleLearningModule, chatWithCoach, getInternationalInfo, getPathConfig } from '@/utils/api.js'
	
	export default {
		data() {
			return {
				testCompleted: false,
				currentLevel: '',
				targets: [],
				selectedTargetIndex: 0,
				scrollTop: 0,
				inputText: '',
				learningModules: [],
				chatMessages: [],
				quickPrompts: [],
				loading: false
			}
		},
		async onLoad() {
			// 检查是否完成测试
			const completed = uni.getStorageSync('testCompleted')
			if (completed) {
				this.testCompleted = true
				const result = uni.getStorageSync('testResult')
				if (result) {
					this.currentLevel = result.level
				}
			}
			
			// 加载页面配置
			await this.loadConfig()
			
			// 加载学习模块
			await this.loadModules()
			
			// 加载当前水平
			await this.loadCurrentLevel()
		},
		methods: {
			async loadConfig() {
				try {
					const config = await getPathConfig()
					this.targets = config.targets || []
					this.quickPrompts = config.quick_prompts || []
					
					// 设置初始欢迎消息
					if (config.welcome_message) {
						this.chatMessages = [
							{
								type: 'ai',
								text: config.welcome_message
							}
						]
					}
				} catch (error) {
					console.error('加载配置失败:', error)
					uni.showToast({
						title: '加载配置失败，请重试',
						icon: 'none'
					})
					// 如果加载失败，保持空数组，不显示任何内容
					this.targets = []
					this.quickPrompts = []
					this.chatMessages = []
				}
			},
			async loadCurrentLevel() {
				try {
					const info = await getInternationalInfo()
					if (info.level) {
						this.currentLevel = info.level
					}
				} catch (error) {
					console.error('加载当前水平失败:', error)
				}
			},
			async loadModules() {
				this.loading = true
				try {
					const modules = await getLearningModules()
					this.learningModules = (modules || []).map(m => ({
						id: m.id,
						name: m.name,
						description: m.description,
						tag: m.tag,
						tagType: m.tag_type,
						added: m.added
					}))
				} catch (error) {
					console.error('加载学习模块失败:', error)
					uni.showToast({
						title: '加载失败',
						icon: 'none'
					})
				} finally {
					this.loading = false
				}
			},
			goToTest() {
				uni.switchTab({
					url: '/pages/international/test'
				})
			},
			onTargetChange(e) {
				this.selectedTargetIndex = e.detail.value
			},
			async toggleModule(index) {
				const module = this.learningModules[index]
				try {
					const result = await toggleLearningModule(module.id)
					module.added = !module.added
					uni.showToast({
						title: result.message || (module.added ? '已加入计划' : '已移除'),
						icon: 'success'
					})
				} catch (error) {
					console.error('切换模块状态失败:', error)
					uni.showToast({
						title: error.data?.detail || '操作失败',
						icon: 'none'
					})
				}
			},
			sendQuickPrompt(prompt) {
				this.inputText = prompt
				this.sendMessage()
			},
			async sendMessage() {
				if (!this.inputText.trim()) return

				// 添加用户消息
				this.chatMessages.push({
					type: 'user',
					text: this.inputText
				})
				
				const userMessage = this.inputText
				this.inputText = ''
				this.scrollTop = 9999

				try {
					// 调用AI对话API
					const response = await chatWithCoach(userMessage)
					
					// 添加AI回复
					this.chatMessages.push({
						type: 'ai',
						text: response.reply
					})
					this.scrollTop = 9999
				} catch (error) {
					console.error('AI对话失败:', error)
					// 添加错误提示
					this.chatMessages.push({
						type: 'ai',
						text: '抱歉，我现在无法回复，请稍后再试。'
					})
					this.scrollTop = 9999
				}
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

	.tip-banner {
		background-color: #FFF3E0;
		border-left: 6rpx solid #FF9800;
		border-radius: 12rpx;
		padding: 24rpx;
		margin-bottom: 40rpx;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.tip-text {
		flex: 1;
		font-size: 26rpx;
		color: #666;
	}

	.tip-btn {
		background-color: #FF9800;
		color: #FFFFFF;
		border: none;
		border-radius: 20rpx;
		padding: 12rpx 24rpx;
		font-size: 24rpx;
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

	.path-section {
		margin-bottom: 60rpx;
	}

	.path-header {
		background-color: #FFFFFF;
		border-radius: 24rpx;
		padding: 32rpx;
		margin-bottom: 32rpx;
		box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
	}

	.current-level {
		display: block;
		font-size: 28rpx;
		color: #2F5D62;
		margin-bottom: 24rpx;
		font-weight: 500;
	}

	.target-selector {
		display: flex;
		align-items: center;
	}

	.target-label {
		font-size: 28rpx;
		color: #666;
		margin-right: 16rpx;
	}

	.target-picker {
		flex: 1;
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 16rpx 24rpx;
		background-color: #FAFAFA;
		border-radius: 12rpx;
		border: 1rpx solid #E0E0E0;
		font-size: 26rpx;
		color: #333;
	}

	.picker-arrow {
		font-size: 32rpx;
		color: #B0B0B0;
	}

	.modules-grid {
		display: flex;
		flex-direction: column;
		gap: 24rpx;
	}

	.module-card {
		background-color: #FFFFFF;
		border-radius: 24rpx;
		padding: 40rpx;
		box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
		border: 2rpx solid #F0F0F0;
		transition: all 0.3s ease;
	}

	.module-card.added {
		border-color: #2F5D62;
		background-color: #F0F7F8;
	}

	.module-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 16rpx;
	}

	.module-name {
		font-size: 32rpx;
		font-weight: 500;
		color: #2F5D62;
	}

	.module-tag {
		font-size: 22rpx;
		padding: 6rpx 12rpx;
		border-radius: 8rpx;
	}

	.module-tag.recommended {
		background-color: #E8F5E9;
		color: #4CAF50;
	}

	.module-tag.optional {
		background-color: #E3F2FD;
		color: #2196F3;
	}

	.module-desc {
		display: block;
		font-size: 26rpx;
		color: #666;
		line-height: 1.6;
		margin-bottom: 24rpx;
	}

	.module-btn {
		width: 100%;
		background-color: #FFFFFF;
		border: 2rpx solid #2F5D62;
		color: #2F5D62;
		border-radius: 50rpx;
		padding: 16rpx;
		font-size: 26rpx;
	}

	.module-btn.added {
		background-color: #2F5D62;
		color: #FFFFFF;
	}

	.coach-section {
		background-color: #FFFFFF;
		border-radius: 24rpx;
		padding: 40rpx;
		box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
		min-height: 600rpx;
		display: flex;
		flex-direction: column;
	}

	.coach-title {
		font-size: 32rpx;
		font-weight: 500;
		color: #2F5D62;
		margin-bottom: 32rpx;
	}

	.chat-messages {
		flex: 1;
		max-height: 400rpx;
		margin-bottom: 32rpx;
	}

	.message-item {
		margin-bottom: 24rpx;
		display: flex;
	}

	.message-item.ai {
		justify-content: flex-start;
	}

	.message-item.user {
		justify-content: flex-end;
	}

	.message-text {
		max-width: 70%;
		padding: 20rpx 24rpx;
		border-radius: 20rpx;
		font-size: 28rpx;
		line-height: 1.6;
	}

	.message-item.ai .message-text {
		background-color: #F5F5F5;
		color: #333;
	}

	.message-item.user .message-text {
		background-color: #E3F2FD;
		color: #2F5D62;
	}

	.chat-input-area {
		border-top: 1rpx solid #F0F0F0;
		padding-top: 24rpx;
	}

	.quick-prompts {
		display: flex;
		flex-wrap: wrap;
		gap: 12rpx;
		margin-bottom: 20rpx;
	}

	.prompt-btn {
		background-color: #FAFAFA;
		border: 1rpx solid #E0E0E0;
		color: #666;
		border-radius: 20rpx;
		padding: 12rpx 20rpx;
		font-size: 24rpx;
	}

	.input-row {
		display: flex;
		gap: 16rpx;
		align-items: center;
	}

	.chat-input {
		flex: 1;
		padding: 20rpx 24rpx;
		background-color: #FAFAFA;
		border-radius: 50rpx;
		border: 1rpx solid #E0E0E0;
		font-size: 28rpx;
	}

	.send-btn {
		background-color: #2F5D62;
		color: #FFFFFF;
		border: none;
		border-radius: 50rpx;
		padding: 20rpx 40rpx;
		font-size: 28rpx;
	}
</style>

