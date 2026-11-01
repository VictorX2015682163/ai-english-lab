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
					<view v-if="currentQuestion.type === 'choice'" class="options-list">
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
							:value="fillAnswer"
							@input="handleInput"
							placeholder="请输入答案"
							placeholder-style="color: #B0B0B0"
							:maxlength="100"
							:focus="inputFocus"
							@focus="onInputFocus"
							@blur="onInputBlur"
							@tap="onInputTap"
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
		</view>
	</view>
</template>

<script>
	import { startPractice, getPracticeQuestions, submitAnswer, endPractice, addWrongQuestion } from '@/utils/api.js'
	
	export default {
		data() {
			return {
				practiceInfo: {},
				sessionId: null,
				currentIndex: 0,
				selectedAnswer: '',
				fillAnswer: '',
				inputFocus: false,
				showFeedback: false,
				feedbackType: '',
				addToWrongBook: false,
				questions: [],
				loading: false
			}
		},
		computed: {
			currentQuestion() {
				if (this.questions.length > 0 && this.currentIndex < this.questions.length) {
					return this.questions[this.currentIndex]
				}
				return null
			}
		},
		async onLoad() {
			// 从本地存储获取练习信息
			const info = uni.getStorageSync('practiceInfo')
			if (info) {
				this.practiceInfo = info
				await this.loadPractice()
			} else {
				// 如果没有信息，返回选择页
				uni.switchTab({
					url: '/pages/public/grade-select'
				})
			}
		},
		methods: {
			async loadPractice() {
				this.loading = true
				try {
					// 开始练习会话
					const response = await startPractice(
						this.practiceInfo.grade,
						this.practiceInfo.version,
						this.practiceInfo.unit
					)
					this.sessionId = response.session_id
					this.questions = (response.questions || []).map(q => ({
						id: q.id,
						type: q.question_type,
						question: q.question,
						options: q.options,
						correctAnswer: q.correct_answer,
						explanation: q.explanation,
						encouragement: q.encouragement
					}))
					
					// 检查是否有题目
					if (!this.questions || this.questions.length === 0) {
						uni.showToast({
							title: '未找到练习题，请重新选择',
							icon: 'none',
							duration: 2000
						})
						setTimeout(() => {
							uni.switchTab({
								url: '/pages/public/grade-select'
							})
						}, 2000)
						return
					}
				} catch (error) {
					console.error('加载练习失败:', error)
					uni.showToast({
						title: error.data?.detail || '加载失败',
						icon: 'none'
					})
					// 发生错误时返回选择页
					setTimeout(() => {
						uni.switchTab({
							url: '/pages/public/grade-select'
						})
					}, 2000)
				} finally {
					this.loading = false
				}
			},
			handleInput(e) {
				this.fillAnswer = e.detail.value
			},
			onInputTap() {
				this.inputFocus = true
			},
			onInputFocus() {
				this.inputFocus = true
				console.log('input focused')
			},
			onInputBlur() {
				this.inputFocus = false
				console.log('input blurred')
			},
			selectAnswer(option) {
				this.selectedAnswer = option
			},
			async submitAnswer() {
				if (!this.currentQuestion || !this.sessionId) return
				
				let userAnswer = ''
				if (this.currentQuestion.type === 'choice') {
					if (!this.selectedAnswer) {
						uni.showToast({
							title: '请选择答案',
							icon: 'none'
						})
						return
					}
					userAnswer = this.selectedAnswer
				} else {
					if (!this.fillAnswer.trim()) {
						uni.showToast({
							title: '请输入答案',
							icon: 'none'
						})
						return
					}
					userAnswer = this.fillAnswer.trim()
				}
				
				try {
					const result = await submitAnswer(
						this.sessionId,
						this.currentQuestion.id,
						userAnswer
					)
					
					this.feedbackType = result.is_correct ? 'correct' : 'wrong'
					this.showFeedback = true
					
					// 更新题目信息（用于显示反馈）
					this.currentQuestion.correctAnswer = result.correct_answer
					this.currentQuestion.explanation = result.explanation
					this.currentQuestion.encouragement = result.encouragement
				} catch (error) {
					console.error('提交答案失败:', error)
					uni.showToast({
						title: error.data?.detail || '提交失败',
						icon: 'none'
					})
				}
			},
			async toggleWrongBook(e) {
				this.addToWrongBook = e.detail.value
				// 当用户勾选"加入错题本"且答题错误时，立即保存
				if (this.addToWrongBook && this.feedbackType === 'wrong') {
					const userAnswer = this.currentQuestion.type === 'choice' 
						? this.selectedAnswer 
						: this.fillAnswer.trim()
					await this.saveToWrongBook(userAnswer)
				}
			},
			async saveToWrongBook(userAnswer) {
				try {
					await addWrongQuestion({
						question_id: this.currentQuestion.id,
						question_type: this.currentQuestion.type,
						question: this.currentQuestion.question,
						options: this.currentQuestion.options,
						correct_answer: this.currentQuestion.correctAnswer,
						user_answer: userAnswer,
						explanation: this.currentQuestion.explanation,
						grade: this.practiceInfo.grade,
						version: this.practiceInfo.version,
						unit: this.practiceInfo.unit
					})
					uni.showToast({
						title: '已加入错题本',
						icon: 'success'
					})
				} catch (error) {
					console.error('保存错题失败:', error)
				}
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
				this.inputFocus = false
				this.showFeedback = false
				this.addToWrongBook = false
				// 延迟重置焦点，确保输入框可以重新获取焦点
				this.$nextTick(() => {
					setTimeout(() => {
						if (this.currentQuestion && this.currentQuestion.type === 'fill') {
							this.inputFocus = true
						}
					}, 100)
				})
			},
			switchGrade() {
				uni.switchTab({
					url: '/pages/public/grade-select'
				})
			},
			async endPractice() {
				uni.showModal({
					title: '结束练习',
					content: '确定要结束本轮练习吗？',
					success: async (res) => {
						if (res.confirm && this.sessionId) {
							try {
								await endPractice(this.sessionId)
								uni.switchTab({
									url: '/pages/mylearning/index'
								})
							} catch (error) {
								console.error('结束练习失败:', error)
								// 即使失败也跳转
								uni.switchTab({
									url: '/pages/mylearning/index'
								})
							}
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
		padding: 24rpx;
		border: 2rpx solid #E0E0E0;
		border-radius: 12rpx;
		font-size: 28rpx;
		background-color: #FFFFFF;
		color: #333;
		box-sizing: border-box;
		line-height: 1.5;
		-webkit-appearance: none;
		appearance: none;
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

	.wrong-book-checkbox {
		display: flex;
		align-items: center;
		font-size: 26rpx;
		color: #666;
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

