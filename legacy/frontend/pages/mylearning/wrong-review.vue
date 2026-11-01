<template>
	<view class="container">
		<view class="content">
			<!-- 顶部进度 -->
			<view class="progress-section">
				<text class="progress-text">{{ currentIndex + 1 }} / {{ questionList.length }}</text>
				<view class="progress-bar">
					<view class="progress-fill" :style="{ width: progress + '%' }"></view>
				</view>
			</view>

			<!-- 题目卡片 -->
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
							:class="{ 
								selected: selectedAnswer === option,
								correct: showAnswer && option === currentQuestion.correctAnswer,
								wrong: showAnswer && selectedAnswer === option && option !== currentQuestion.correctAnswer
							}"
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
							:disabled="showAnswer"
							:readonly="showAnswer"
						/>
						<view class="correct-answer-hint" v-if="showAnswer">
							<text class="hint-text">正确答案：{{ currentQuestion.correctAnswer }}</text>
						</view>
					</view>
				</view>

				<!-- 反馈区域 -->
				<view class="feedback-section" v-if="showAnswer">
					<view class="feedback-header" :class="feedbackType">
						<text class="feedback-icon">{{ feedbackType === 'correct' ? '✓' : '✗' }}</text>
						<text class="feedback-title">{{ feedbackType === 'correct' ? '回答正确！' : '回答错误' }}</text>
					</view>
					<text class="feedback-explanation" v-if="currentQuestion.explanation">{{ currentQuestion.explanation }}</text>
				</view>
			</view>

			<!-- 操作按钮 -->
			<view class="action-buttons">
				<button 
					class="action-btn submit-btn" 
					v-if="!showAnswer"
					@click="submitAnswer"
					:disabled="!hasAnswer"
				>
					提交答案
				</button>
				<button 
					class="action-btn next-btn" 
					v-else
					@click="nextQuestion"
				>
					{{ currentIndex === questionList.length - 1 ? '完成复习' : '下一题' }}
				</button>
			</view>

			<!-- 完成提示 -->
			<view class="complete-section" v-if="completed">
				<text class="complete-icon">🎉</text>
				<text class="complete-title">复习完成！</text>
				<text class="complete-desc">本次答对了 {{ correctCount }} / {{ questionList.length }} 道题</text>
				<view class="complete-stats">
					<text class="stats-text">正确率：{{ accuracy }}%</text>
				</view>
				<button class="complete-btn" @click="goBack">返回错题本</button>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				questionList: [],
				currentIndex: 0,
				selectedAnswer: '',
				fillAnswer: '',
				showAnswer: false,
				completed: false,
				correctCount: 0,
				reviewResults: []
			}
		},
		computed: {
			currentQuestion() {
				return this.questionList[this.currentIndex] || null
			},
			progress() {
				return this.questionList.length > 0 ? ((this.currentIndex + 1) / this.questionList.length) * 100 : 0
			},
			hasAnswer() {
				if (!this.currentQuestion) return false
				if (this.currentQuestion.type === 'choice') {
					return this.selectedAnswer !== ''
				} else {
					return (this.fillAnswer || '').trim() !== ''
				}
			},
			feedbackType() {
				if (!this.currentQuestion || !this.showAnswer) return ''
				let isCorrect = false
				if (this.currentQuestion.type === 'choice') {
					isCorrect = this.selectedAnswer === this.currentQuestion.correctAnswer
				} else {
					const userAnswer = (this.fillAnswer || '').trim().toLowerCase()
					const correctAnswer = (this.currentQuestion.correctAnswer || '').trim().toLowerCase()
					isCorrect = userAnswer === correctAnswer
				}
				return isCorrect ? 'correct' : 'wrong'
			},
			accuracy() {
				if (this.questionList.length === 0) return 0
				return Math.round((this.correctCount / this.questionList.length) * 100)
			}
		},
		onLoad() {
			this.loadQuestions()
		},
		methods: {
			loadQuestions() {
				const wrongs = uni.getStorageSync('wrongBook') || []
				if (wrongs.length === 0) {
					uni.showToast({
						title: '错题本为空',
						icon: 'none'
					})
					setTimeout(() => {
						uni.navigateBack()
					}, 1500)
					return
				}
				// 打乱顺序，重新生成题目（基于错题）
				this.questionList = this.generateQuestions(wrongs)
			},
			generateQuestions(wrongs) {
				// 基于错题生成新的类似题目
				return wrongs
					.filter(wrong => wrong && wrong.question && wrong.correctAnswer) // 过滤无效数据
					.map((wrong, index) => {
						const questionType = wrong.type || 'choice'
						const newQuestion = {
							id: wrong.id || wrong.time || Date.now() + index,
							type: questionType,
							question: wrong.question,
							correctAnswer: wrong.correctAnswer,
							explanation: wrong.explanation || '',
							encouragement: wrong.encouragement || '很好！继续加油！'
						}
						
						// 如果是选择题，必须确保有选项
						if (questionType === 'choice') {
							if (wrong.options && Array.isArray(wrong.options) && wrong.options.length > 0) {
								newQuestion.options = [...wrong.options]
							} else {
								// 如果没有选项，转换为填空题
								newQuestion.type = 'fill'
							}
						}
						
						return newQuestion
					})
			},
			selectAnswer(option) {
				if (this.showAnswer) return
				this.selectedAnswer = option
			},
			submitAnswer() {
				if (!this.hasAnswer || !this.currentQuestion) return
				
				this.showAnswer = true
				
				let isCorrect = false
				if (this.currentQuestion.type === 'choice') {
					isCorrect = this.selectedAnswer === this.currentQuestion.correctAnswer
				} else {
					const userAnswer = (this.fillAnswer || '').trim().toLowerCase()
					const correctAnswer = (this.currentQuestion.correctAnswer || '').trim().toLowerCase()
					isCorrect = userAnswer === correctAnswer
				}
				
				if (isCorrect) {
					this.correctCount++
				}
				
				this.reviewResults.push({
					questionId: this.currentQuestion.id,
					correct: isCorrect
				})
			},
			nextQuestion() {
				// 如果当前是最后一题，标记完成
				if (this.currentIndex >= this.questionList.length - 1) {
					this.completed = true
					this.updateWrongBook()
					return
				}
				// 否则进入下一题
				if (this.currentIndex < this.questionList.length - 1) {
					this.currentIndex++
					this.resetAnswer()
				}
			},
			resetAnswer() {
				this.selectedAnswer = ''
				this.fillAnswer = ''
				this.showAnswer = false
			},
			updateWrongBook() {
				// 如果答对了，可以从错题本中移除（可选）
				// 这里我们保留错题，但可以标记为已复习
				const wrongs = uni.getStorageSync('wrongBook') || []
				this.reviewResults.forEach(result => {
					if (!result || !result.questionId) return
					const wrong = wrongs.find(w => {
						const wId = w.id || w.time
						return wId && wId.toString() === result.questionId.toString()
					})
					if (wrong && result.correct) {
						wrong.reviewed = true
						wrong.lastReviewAt = new Date().toISOString()
					}
				})
				uni.setStorageSync('wrongBook', wrongs)
			},
			goBack() {
				uni.navigateBack()
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
		padding: 40rpx;
		width: 100%;
		box-sizing: border-box;
	}

	.progress-section {
		width: 100%;
		margin-bottom: 40rpx;
	}

	.progress-text {
		display: block;
		text-align: center;
		font-size: 28rpx;
		color: #666;
		margin-bottom: 16rpx;
	}

	.progress-bar {
		width: 100%;
		height: 8rpx;
		background-color: #E0E0E0;
		border-radius: 4rpx;
		overflow: hidden;
	}

	.progress-fill {
		height: 100%;
		background-color: #2F5D62;
		transition: width 0.3s ease;
	}

	.question-card {
		background-color: #FFFFFF;
		border-radius: 24rpx;
		padding: 48rpx 40rpx;
		box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
		margin-bottom: 40rpx;
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
		margin-bottom: 32rpx;
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

	.option-item.correct {
		border-color: #4CAF50;
		background-color: #E8F5E9;
	}

	.option-item.wrong {
		border-color: #FF5252;
		background-color: #FFE5E5;
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
		min-height: 80rpx;
		display: block;
	}

	.correct-answer-hint {
		margin-top: 16rpx;
		padding: 16rpx;
		background-color: #E8F5E9;
		border-radius: 12rpx;
	}

	.hint-text {
		font-size: 26rpx;
		color: #4CAF50;
	}

	.feedback-section {
		padding-top: 32rpx;
		border-top: 1rpx solid #F0F0F0;
	}

	.feedback-header {
		display: flex;
		align-items: center;
		margin-bottom: 16rpx;
	}

	.feedback-header.correct {
		color: #4CAF50;
	}

	.feedback-header.wrong {
		color: #FF9800;
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

	.feedback-header.correct .feedback-icon {
		background-color: #E8F5E9;
	}

	.feedback-header.wrong .feedback-icon {
		background-color: #FFF3E0;
	}

	.feedback-title {
		font-size: 32rpx;
		font-weight: 500;
	}

	.feedback-explanation {
		display: block;
		font-size: 26rpx;
		color: #999;
		line-height: 1.6;
	}

	.action-buttons {
		width: 100%;
	}

	.action-btn {
		width: 100%;
		padding: 28rpx;
		border-radius: 50rpx;
		font-size: 32rpx;
		border: none;
	}

	.submit-btn {
		background-color: #2F5D62;
		color: #FFFFFF;
	}

	.submit-btn:disabled {
		background-color: #E0E0E0;
		color: #B0B0B0;
	}

	.next-btn {
		background-color: #2F5D62;
		color: #FFFFFF;
	}

	.complete-section {
		width: 100%;
		text-align: center;
		padding: 80rpx 40rpx;
	}

	.complete-icon {
		display: block;
		font-size: 120rpx;
		margin-bottom: 32rpx;
	}

	.complete-title {
		display: block;
		font-size: 44rpx;
		font-weight: 500;
		color: #2F5D62;
		margin-bottom: 16rpx;
	}

	.complete-desc {
		display: block;
		font-size: 28rpx;
		color: #666;
		margin-bottom: 24rpx;
	}

	.complete-stats {
		margin-bottom: 60rpx;
	}

	.stats-text {
		font-size: 32rpx;
		color: #2F5D62;
		font-weight: 500;
	}

	.complete-btn {
		width: 100%;
		background-color: #2F5D62;
		color: #FFFFFF;
		border: none;
		border-radius: 50rpx;
		padding: 24rpx;
		font-size: 32rpx;
	}
</style>

