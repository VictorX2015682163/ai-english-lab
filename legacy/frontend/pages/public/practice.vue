<template>
	<view class="container">
		<!-- 顶部信息栏 -->
		<view class="top-bar">
			<view class="info-section">
				<text class="info-text">{{ practiceInfo.grade }} · {{ practiceInfo.version }} · {{ practiceInfo.unit }}</text>
				<text class="question-count">{{ currentIndex + 1 }} / {{ questions.length }}</text>
			</view>
			<button class="switch-btn" @click="switchGrade">切换年级/单元</button>
		</view>

		<view class="content">
			<!-- 题目区域 -->
			<view class="question-card" v-if="currentQuestion">
				<view class="question-header">
					<text class="question-type">{{ currentQuestion.type === 'choice' ? '选择题' : '填空题' }}</text>
				</view>
				<view class="question-body">
					<text class="question-text">{{ currentQuestion.question }}</text>
					
					<!-- 选择题 -->
					<view v-if="currentQuestion.type === 'choice' && currentQuestion.options && currentQuestion.options.length > 0" class="options-list">
						<view 
							v-for="(option, index) in currentQuestion.options" 
							:key="index"
							class="option-item"
							:class="{ selected: selectedAnswer === option }"
							@click="selectAnswer(option)"
						>
							<text class="option-label">{{ String.fromCharCode(65 + index) }}.</text>
							<text class="option-text">{{ option }}</text>
						</view>
					</view>

					<!-- 填空题 -->
					<view v-else class="fill-blank">
						<input 
							class="answer-input" 
							type="text"
							v-model="fillAnswer"
							placeholder="请输入答案"
							placeholder-style="color: #B0B0B0"
							:maxlength="100"
							:disabled="false"
							:readonly="false"
						/>
					</view>
				</view>

				<view class="question-footer">
					<button class="submit-btn" @click="submitAnswer">提交本题</button>
					<text class="skip-btn" @click="nextQuestion">跳过</text>
				</view>
			</view>

			<!-- 反馈区域 -->
			<view class="feedback-card" v-if="showFeedback" :class="feedbackType">
				<view class="feedback-header">
					<text class="feedback-icon">{{ feedbackType === 'correct' ? '✓' : '✗' }}</text>
					<text class="feedback-title">{{ feedbackType === 'correct' ? '回答正确！' : '回答错误' }}</text>
				</view>
				<view class="feedback-body">
					<text class="feedback-text" v-if="feedbackType === 'correct'">{{ currentQuestion.encouragement }}</text>
					<view v-else>
						<text class="feedback-text">正确答案：{{ currentQuestion.correctAnswer }}</text>
						<text class="feedback-explanation">{{ currentQuestion.explanation }}</text>
					</view>
				</view>
				<view class="feedback-footer">
					<label class="wrong-book-checkbox">
						<checkbox 
							:checked="addToWrongBook" 
							@change="toggleWrongBook"
							color="#2F5D62"
						/>
						<text>加入错题本</text>
					</label>
					<button class="add-word-btn" @click="showAddWordModal">+ 添加生词</button>
				</view>
			</view>

			<!-- 控制按钮 -->
			<view class="control-buttons">
				<button 
					class="nav-btn" 
					:disabled="currentIndex === 0"
					@click="prevQuestion"
				>
					上一题
				</button>
				<button 
					class="nav-btn" 
					:disabled="currentIndex === questions.length - 1"
					@click="nextQuestion"
				>
					下一题
				</button>
			</view>

			<view class="end-section">
				<button class="end-btn" @click="endPractice">结束本轮练习</button>
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
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				practiceInfo: {},
				currentIndex: 0,
				selectedAnswer: '',
				fillAnswer: '',
				showFeedback: false,
				feedbackType: '',
				addToWrongBook: false,
				showWordModal: false,
				newWord: {
					word: '',
					phonetic: '',
					meaning: '',
					example: ''
				},
				questions: [
					{
						type: 'choice',
						question: 'What is the past tense of "go"?',
						options: ['goed', 'went', 'gone', 'going'],
						correctAnswer: 'went',
						explanation: '"go" 的过去式是 "went"，这是一个不规则动词。',
						encouragement: '很好！你掌握了这个不规则动词的变化。'
					},
					{
						type: 'choice',
						question: 'I _____ to school every day.',
						options: ['go', 'goes', 'went', 'going'],
						correctAnswer: 'go',
						explanation: '一般现在时，主语是 "I"，所以用动词原形 "go"。',
						encouragement: '正确！你理解了一般现在时的用法。'
					},
					{
						type: 'fill',
						question: 'Complete the sentence: She _____ (like) reading books.',
						correctAnswer: 'likes',
						explanation: '第三人称单数主语 "She" 后面，动词要加 "s"。',
						encouragement: '完美！你掌握了第三人称单数的用法。'
					},
					{
						type: 'choice',
						question: 'Which word means "happy"?',
						options: ['sad', 'angry', 'glad', 'tired'],
						correctAnswer: 'glad',
						explanation: '"glad" 意思是 "高兴的"，与 "happy" 同义。',
						encouragement: '很棒！你的词汇量不错。'
					},
					{
						type: 'fill',
						question: 'Fill in the blank: There _____ (be) many students in the classroom.',
						correctAnswer: 'are',
						explanation: '"many students" 是复数，所以用 "are"。',
						encouragement: '正确！你理解了 there be 句型的用法。'
					}
				]
			}
		},
		computed: {
			currentQuestion() {
				if (this.questions && this.questions.length > 0 && this.currentIndex >= 0 && this.currentIndex < this.questions.length) {
					return this.questions[this.currentIndex]
				}
				return null
			}
		},
		onLoad() {
			// 从本地存储获取练习信息
			const info = uni.getStorageSync('practiceInfo')
			if (info) {
				this.practiceInfo = info
			} else {
				// 如果没有信息，使用默认值
				this.practiceInfo = {
					grade: '六年级',
					version: '人教版',
					unit: 'Unit 3'
				}
			}
		},
		methods: {
			selectAnswer(option) {
				this.selectedAnswer = option
			},
			submitAnswer() {
				if (!this.currentQuestion) return
				
				let isCorrect = false
				if (this.currentQuestion.type === 'choice') {
					isCorrect = this.selectedAnswer === this.currentQuestion.correctAnswer
				} else {
					const userAnswer = (this.fillAnswer || '').trim().toLowerCase()
					const correctAnswer = (this.currentQuestion.correctAnswer || '').trim().toLowerCase()
					isCorrect = userAnswer === correctAnswer
				}

				this.feedbackType = isCorrect ? 'correct' : 'wrong'
				this.showFeedback = true

				// 如果错误且勾选了错题本，保存到错题本
				if (!isCorrect && this.addToWrongBook) {
					// 延迟保存，确保状态已更新
					setTimeout(() => {
						this.saveToWrongBook()
					}, 200)
				}
			},
			toggleWrongBook(e) {
				const newValue = e.detail.value
				this.addToWrongBook = newValue
				
				// 显示调试信息
				uni.showToast({
					title: `勾选状态: ${newValue ? '已勾选' : '未勾选'}`,
					icon: 'none',
					duration: 1000
				})
				
				// 如果用户勾选了错题本，立即保存
				// 因为 checkbox 只在回答错误时才会显示
				if (newValue) {
					// 延迟一下确保状态更新
					setTimeout(() => {
						this.saveToWrongBook()
					}, 200)
				}
			},
			saveToWrongBook() {
				// 显示开始保存的提示
				uni.showToast({
					title: '开始保存错题...',
					icon: 'loading',
					duration: 500
				})
				
				if (!this.currentQuestion) {
					setTimeout(() => {
						uni.showToast({
							title: '保存失败：题目信息缺失',
							icon: 'none'
						})
					}, 500)
					return
				}
				
				// 保存错题到本地存储
				let wrongBook = uni.getStorageSync('wrongBook') || []
				
				// 生成唯一标识
				const questionId = this.currentQuestion.id || (this.currentQuestion.question + '_' + this.currentQuestion.correctAnswer)
				
				// 检查是否已存在相同的错题（通过题目和正确答案判断）
				const exists = wrongBook.some(w => {
					if (!w || !w.question || !w.correctAnswer) return false
					return w.question === this.currentQuestion.question && 
						   w.correctAnswer === this.currentQuestion.correctAnswer
				})
				
				if (exists) {
					uni.showToast({
						title: '该错题已存在',
						icon: 'none',
						duration: 1500
					})
					return
				}
				
				// 构建错题对象，确保所有必要字段都存在
				const wrongItem = {
					id: questionId + '_' + Date.now(), // 确保唯一ID
					type: this.currentQuestion.type || 'choice',
					question: this.currentQuestion.question || '',
					correctAnswer: this.currentQuestion.correctAnswer || '',
					explanation: this.currentQuestion.explanation || '',
					encouragement: this.currentQuestion.encouragement || '',
					userAnswer: this.currentQuestion.type === 'choice' ? (this.selectedAnswer || '') : (this.fillAnswer || ''),
					time: new Date().toISOString()
				}
				
				// 如果是选择题，保留选项
				if (this.currentQuestion.type === 'choice' && this.currentQuestion.options) {
					wrongItem.options = [...this.currentQuestion.options]
				}
				
				wrongBook.push(wrongItem)
				uni.setStorageSync('wrongBook', wrongBook)
				
				// 验证保存是否成功
				const verify = uni.getStorageSync('wrongBook') || []
				setTimeout(() => {
					if (verify.length >= wrongBook.length) {
						uni.showToast({
							title: `已加入错题本 (共${verify.length}题)`,
							icon: 'success',
							duration: 2000
						})
					} else {
						uni.showToast({
							title: `保存失败 (期望${wrongBook.length}，实际${verify.length})`,
							icon: 'none',
							duration: 3000
						})
					}
				}, 500)
			},
			nextQuestion() {
				if (this.currentIndex < this.questions.length - 1) {
					this.currentIndex++
					this.resetAnswer()
				}
			},
			prevQuestion() {
				if (this.currentIndex > 0) {
					this.currentIndex--
					this.resetAnswer()
				}
			},
			resetAnswer() {
				this.selectedAnswer = ''
				this.fillAnswer = ''
				this.showFeedback = false
				this.addToWrongBook = false
			},
			showAddWordModal() {
				if (!this.currentQuestion) return
				
				// 从题目中提取可能的单词
				const questionText = this.currentQuestion.question || ''
				// 尝试提取正确答案作为单词
				const correctAnswer = this.currentQuestion.correctAnswer || ''
				
				this.newWord = {
					word: correctAnswer,
					phonetic: '',
					meaning: '',
					example: questionText
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
			},
			switchGrade() {
				uni.switchTab({
					url: '/pages/public/grade-select'
				})
			},
			endPractice() {
				uni.showModal({
					title: '结束练习',
					content: '确定要结束本轮练习吗？',
					success: (res) => {
						if (res.confirm) {
							uni.switchTab({
								url: '/pages/mylearning/index'
							})
						}
					}
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

	.top-bar {
		background-color: #FFFFFF;
		padding: 24rpx 40rpx;
		display: flex;
		justify-content: space-between;
		align-items: center;
		border-bottom: 1rpx solid #F0F0F0;
		width: 100%;
		box-sizing: border-box;
	}

	.info-section {
		display: flex;
		flex-direction: column;
	}

	.info-text {
		font-size: 26rpx;
		color: #666;
		margin-bottom: 8rpx;
	}

	.question-count {
		font-size: 24rpx;
		color: #999;
	}

	.switch-btn {
		background-color: transparent;
		border: 1rpx solid #E0E0E0;
		color: #666;
		font-size: 24rpx;
		padding: 12rpx 24rpx;
		border-radius: 20rpx;
	}

	.content {
		flex: 1;
		padding: 40rpx;
		width: 100%;
		box-sizing: border-box;
		overflow-y: auto;
		-webkit-overflow-scrolling: touch;
	}

	.question-card {
		background-color: #FFFFFF;
		border-radius: 24rpx;
		padding: 48rpx 40rpx;
		margin-bottom: 40rpx;
		box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
	}

	.question-header {
		margin-bottom: 32rpx;
	}

	.question-type {
		font-size: 24rpx;
		color: #2F5D62;
		background-color: #F0F7F8;
		padding: 8rpx 16rpx;
		border-radius: 8rpx;
	}

	.question-body {
		margin-bottom: 40rpx;
	}

	.question-text {
		display: block;
		font-size: 32rpx;
		color: #333;
		line-height: 1.8;
		margin-bottom: 32rpx;
	}

	.options-list {
		display: flex;
		flex-direction: column;
		gap: 20rpx;
	}

	.option-item {
		display: flex;
		align-items: center;
		padding: 24rpx;
		border: 2rpx solid #E0E0E0;
		border-radius: 12rpx;
		background-color: #FAFAFA;
		transition: all 0.3s ease;
	}

	.option-item.selected {
		border-color: #2F5D62;
		background-color: #F0F7F8;
	}

	.option-label {
		font-size: 28rpx;
		color: #2F5D62;
		margin-right: 16rpx;
		font-weight: 500;
	}

	.option-text {
		font-size: 28rpx;
		color: #333;
	}

	.fill-blank {
		margin-top: 24rpx;
	}

	.answer-input {
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
	
	.answer-input:focus {
		border-color: #2F5D62;
		outline: none;
	}

	.question-footer {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding-top: 32rpx;
		border-top: 1rpx solid #F0F0F0;
	}

	.submit-btn {
		background-color: #2F5D62;
		color: #FFFFFF;
		border: none;
		border-radius: 50rpx;
		padding: 20rpx 48rpx;
		font-size: 28rpx;
	}

	.skip-btn {
		font-size: 26rpx;
		color: #B0B0B0;
	}

	.feedback-card {
		background-color: #FFFFFF;
		border-radius: 24rpx;
		padding: 40rpx;
		margin-bottom: 40rpx;
		animation: slideIn 0.3s ease;
	}

	.feedback-card.correct {
		border-left: 6rpx solid #4CAF50;
	}

	.feedback-card.wrong {
		border-left: 6rpx solid #FF9800;
	}

	@keyframes slideIn {
		from {
			opacity: 0;
			transform: translateY(-20rpx);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.feedback-header {
		display: flex;
		align-items: center;
		margin-bottom: 24rpx;
	}

	.feedback-icon {
		width: 48rpx;
		height: 48rpx;
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 32rpx;
		margin-right: 16rpx;
	}

	.feedback-card.correct .feedback-icon {
		background-color: #E8F5E9;
		color: #4CAF50;
	}

	.feedback-card.wrong .feedback-icon {
		background-color: #FFF3E0;
		color: #FF9800;
	}

	.feedback-title {
		font-size: 32rpx;
		font-weight: 500;
	}

	.feedback-card.correct .feedback-title {
		color: #4CAF50;
	}

	.feedback-card.wrong .feedback-title {
		color: #FF9800;
	}

	.feedback-body {
		margin-bottom: 24rpx;
	}

	.feedback-text {
		display: block;
		font-size: 28rpx;
		color: #666;
		line-height: 1.8;
		margin-bottom: 16rpx;
	}

	.feedback-explanation {
		display: block;
		font-size: 26rpx;
		color: #999;
		line-height: 1.6;
	}

	.feedback-footer {
		padding-top: 24rpx;
		border-top: 1rpx solid #F0F0F0;
	}

	.feedback-footer {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.wrong-book-checkbox {
		display: flex;
		align-items: center;
		font-size: 26rpx;
		color: #666;
	}

	.add-word-btn {
		background-color: transparent;
		border: 2rpx solid #2F5D62;
		color: #2F5D62;
		border-radius: 50rpx;
		padding: 12rpx 24rpx;
		font-size: 24rpx;
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

	.control-buttons {
		display: flex;
		justify-content: space-between;
		gap: 20rpx;
		margin-bottom: 40rpx;
	}

	.nav-btn {
		flex: 1;
		background-color: #FFFFFF;
		border: 2rpx solid #E0E0E0;
		color: #666;
		border-radius: 50rpx;
		padding: 24rpx;
		font-size: 28rpx;
	}

	.nav-btn:disabled {
		opacity: 0.5;
	}

	.end-section {
		display: flex;
		justify-content: center;
		padding-bottom: 40rpx;
	}

	.end-btn {
		background-color: transparent;
		border: 2rpx solid #E0E0E0;
		color: #666;
		border-radius: 50rpx;
		padding: 20rpx 48rpx;
		font-size: 28rpx;
	}
</style>

