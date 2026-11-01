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
								<text>{{ targets[selectedTargetIndex] }}</text>
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
						<view class="message-content">
							<text class="message-text">{{ message.text }}</text>
							<button class="add-word-from-message-btn" v-if="message.type === 'ai'" @click="showAddWordFromMessage(message.text)">+ 添加生词</button>
						</view>
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
							:disabled="false"
							:readonly="false"
						/>
						<button class="send-btn" @click="sendMessage">发送</button>
					</view>
				</view>
			</view>

			<!-- 添加生词弹窗 -->
			<view class="modal-overlay" v-if="showWordModal" @click="hideAddWordModal">
				<view class="modal-content" @click.stop>
					<view class="modal-header">
						<text class="modal-title">添加生词</text>
						<text class="modal-close" @click="hideAddWordModal">×</text>
					</view>
					<view class="modal-body">
						<view class="form-group">
							<text class="form-label">单词</text>
							<input 
								class="form-input" 
								type="text"
								v-model="newWord.word"
								placeholder="请输入单词"
								placeholder-style="color: #B0B0B0"
								:disabled="false"
								:readonly="false"
							/>
						</view>
						<view class="form-group">
							<text class="form-label">音标（可选）</text>
							<input 
								class="form-input" 
								type="text"
								v-model="newWord.phonetic"
								placeholder="请输入音标"
								placeholder-style="color: #B0B0B0"
								:disabled="false"
								:readonly="false"
							/>
						</view>
						<view class="form-group">
							<text class="form-label">释义</text>
							<input 
								class="form-input" 
								type="text"
								v-model="newWord.meaning"
								placeholder="请输入释义"
								placeholder-style="color: #B0B0B0"
								:disabled="false"
								:readonly="false"
							/>
						</view>
						<view class="form-group">
							<text class="form-label">例句（可选）</text>
							<input 
								class="form-input" 
								type="text"
								v-model="newWord.example"
								placeholder="请输入例句"
								placeholder-style="color: #B0B0B0"
								:disabled="false"
								:readonly="false"
							/>
						</view>
					</view>
					<view class="modal-footer">
						<button class="modal-btn cancel-btn" @click="hideAddWordModal">取消</button>
						<button class="modal-btn confirm-btn" @click="addWordToBook">确定</button>
					</view>
				</view>
			</view>
		</scroll-view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				testCompleted: false,
				currentLevel: 'B1 Intermediate',
				targets: ['一个学期内达到 B2', '半年内达到 B2', '一年内达到 C1'],
				selectedTargetIndex: 0,
				scrollTop: 0,
				inputText: '',
				showWordModal: false,
				newWord: {
					word: '',
					phonetic: '',
					meaning: '',
					example: ''
				},
				learningModules: [
					{
						name: 'Academic Reading',
						description: '提升学术阅读能力，掌握长篇文章的理解和分析技巧',
						tag: '系统推荐',
						tagType: 'recommended',
						added: true
					},
					{
						name: 'Essay Writing',
						description: '学习写作结构与逻辑，提升学术写作水平',
						tag: '系统推荐',
						tagType: 'recommended',
						added: true
					},
					{
						name: 'Listening & Note-taking',
						description: '训练听力理解能力，掌握快速记笔记的方法',
						tag: '可选模块',
						tagType: 'optional',
						added: false
					},
					{
						name: 'Speaking for Presentation',
						description: '提升演讲表达能力，增强口语流利度和自信',
						tag: '可选模块',
						tagType: 'optional',
						added: false
					}
				],
				chatMessages: [
					{
						type: 'ai',
						text: '你好！我是你的 AI 学习教练。根据你的分级测试结果，我为你推荐了几个重点学习模块。有什么问题随时问我！'
					},
					{
						type: 'user',
						text: '我想先提升阅读能力'
					},
					{
						type: 'ai',
						text: '很好的选择！Academic Reading 模块非常适合你。我们可以从理解文章结构开始，然后逐步提升阅读速度和理解深度。需要我为你安排一节阅读课吗？'
					}
				],
				quickPrompts: [
					'根据我当前水平安排一节阅读课',
					'帮我出 5 道关于旅行的口语题',
					'帮我批改这段作文，并解释修改'
				]
			}
		},
		onLoad() {
			// 检查是否完成测试
			const completed = uni.getStorageSync('testCompleted')
			if (completed) {
				this.testCompleted = true
				const result = uni.getStorageSync('testResult')
				if (result) {
					this.currentLevel = result.level
				}
			}
		},
		methods: {
			goToTest() {
				uni.switchTab({
					url: '/pages/international/test'
				})
			},
			onTargetChange(e) {
				this.selectedTargetIndex = e.detail.value
			},
			toggleModule(index) {
				this.learningModules[index].added = !this.learningModules[index].added
				uni.showToast({
					title: this.learningModules[index].added ? '已加入计划' : '已移除',
					icon: 'success'
				})
			},
			sendQuickPrompt(prompt) {
				this.inputText = prompt
				// 使用 $nextTick 确保数据更新后再发送
				this.$nextTick(() => {
					this.sendMessage()
				})
			},
			sendMessage() {
				const messageText = this.inputText.trim()
				if (!messageText) {
					return
				}

				// 添加用户消息
				this.chatMessages.push({
					type: 'user',
					text: messageText
				})

				// 清空输入框
				this.inputText = ''
				
				// 滚动到底部
				this.$nextTick(() => {
					this.scrollTop = 9999
				})

				// 模拟 AI 回复
				setTimeout(() => {
					this.chatMessages.push({
						type: 'ai',
						text: '好的，我理解了你的需求。让我为你准备相关内容...'
					})
					this.$nextTick(() => {
						this.scrollTop = 9999
					})
				}, 500)
			},
			showAddWordFromMessage(messageText) {
				// 从消息中提取可能的单词（简单实现，可以改进）
				this.newWord = {
					word: '',
					phonetic: '',
					meaning: '',
					example: messageText || ''
				}
				this.showWordModal = true
			},
			hideAddWordModal() {
				this.showWordModal = false
			},
			addWordToBook() {
				if (!this.newWord || !this.newWord.word || !this.newWord.meaning) {
					uni.showToast({
						title: '请填写单词和释义',
						icon: 'none',
						duration: 2000
					})
					return
				}

				const wordText = this.newWord.word.trim()
				const meaningText = this.newWord.meaning.trim()
				
				if (!wordText || !meaningText) {
					uni.showToast({
						title: '请填写单词和释义',
						icon: 'none',
						duration: 2000
					})
					return
				}

				const word = {
					id: Date.now().toString(),
					word: wordText,
					phonetic: (this.newWord.phonetic || '').trim(),
					meaning: meaningText,
					example: (this.newWord.example || '').trim(),
					addedAt: new Date().toISOString(),
					reviewCount: 0,
					lastReviewAt: null
				}

				const words = uni.getStorageSync('wordBook') || []
				// 检查是否已存在
				const exists = words.some(w => w && w.word && w.word.toLowerCase() === word.word.toLowerCase())
				if (exists) {
					uni.showToast({
						title: '该单词已存在',
						icon: 'none'
					})
					return
				}
				
				words.unshift(word)
				uni.setStorageSync('wordBook', words)

				this.hideAddWordModal()
				uni.showToast({
					title: '已添加到生词本',
					icon: 'success'
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

	.message-content {
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		max-width: 70%;
	}

	.message-text {
		width: 100%;
		padding: 20rpx 24rpx;
		border-radius: 20rpx;
		font-size: 28rpx;
		line-height: 1.6;
		margin-bottom: 8rpx;
	}

	.add-word-from-message-btn {
		background-color: transparent;
		border: 1rpx solid #2F5D62;
		color: #2F5D62;
		border-radius: 20rpx;
		padding: 8rpx 16rpx;
		font-size: 22rpx;
		margin-top: 8rpx;
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
		padding: 20rpx 24rpx !important;
		background-color: #FFFFFF;
		border-radius: 50rpx;
		border: 1rpx solid #E0E0E0;
		min-height: 80rpx;
		-webkit-appearance: none;
		appearance: none;
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

	/* 弹窗样式 */
	.modal-overlay {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		background-color: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
	}

	.modal-content {
		background-color: #FFFFFF;
		border-radius: 24rpx;
		width: 90%;
		max-width: 600rpx;
		max-height: 80vh;
		overflow-y: auto;
	}

	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 32rpx;
		border-bottom: 1rpx solid #F0F0F0;
	}

	.modal-title {
		font-size: 32rpx;
		font-weight: 500;
		color: #2F5D62;
	}

	.modal-close {
		font-size: 48rpx;
		color: #999;
		line-height: 1;
	}

	.modal-body {
		padding: 32rpx;
	}

	.form-group {
		margin-bottom: 32rpx;
	}

	.form-label {
		display: block;
		font-size: 28rpx;
		color: #333;
		margin-bottom: 16rpx;
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
		min-height: 80rpx;
	}

	.modal-footer {
		display: flex;
		gap: 16rpx;
		padding: 32rpx;
		border-top: 1rpx solid #F0F0F0;
	}

	.modal-btn {
		flex: 1;
		padding: 24rpx;
		border-radius: 50rpx;
		font-size: 28rpx;
		border: none;
	}

	.cancel-btn {
		background-color: #F5F5F5;
		color: #666;
	}

	.confirm-btn {
		background-color: #2F5D62;
		color: #FFFFFF;
	}
</style>

