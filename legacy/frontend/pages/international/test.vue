<template>
	<view class="container">
		<scroll-view class="content" scroll-y>
			<!-- 顶部标题 -->
			<view class="header-section">
				<text class="main-title">国际学校模式：分级测试</text>
				<text class="sub-title">10–15 道题，帮你找到最合适的起点</text>
			</view>

			<!-- 测试说明区 -->
			<view class="intro-section" v-if="!testStarted">
				<text class="intro-text">通过词汇、语法和阅读小测试，初步判断你的英语等级（参考 A1–C1）。</text>
				<text class="intro-text">完成后 AI 会推荐你该重点学习什么。</text>
				<button class="start-test-btn" @click="startTest">开始测试</button>
			</view>

			<!-- 测试题卡片 -->
			<view class="test-card" v-if="testStarted && !testCompleted">
				<view class="test-header">
					<text class="question-number">第 {{ currentIndex + 1 }} 题 / 共 {{ testQuestions.length }} 题</text>
					<view class="progress-bar">
						<view class="progress-fill" :style="{ width: progress + '%' }"></view>
					</view>
				</view>

				<view class="question-section">
					<text class="question-type-label">{{ currentQuestion.category }}</text>
					<text class="question-text">{{ currentQuestion.question }}</text>
					
					<view class="options-list">
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
				</view>

				<view class="test-footer">
					<button 
						class="next-btn" 
						:disabled="!selectedAnswer"
						@click="nextQuestion"
					>
						{{ currentIndex === testQuestions.length - 1 ? '完成测试' : '下一题' }}
					</button>
				</view>
			</view>

			<!-- 测试完成结果区域 -->
			<view class="result-card" v-if="testCompleted">
				<view class="result-header">
					<text class="result-title">你的初步水平</text>
					<text class="result-level">{{ testResult.level }}</text>
					<text class="result-desc">{{ testResult.description }}</text>
				</view>

				<view class="suggestions-section">
					<text class="suggestions-title">建议项</text>
					<view 
						v-for="(suggestion, index) in testResult.suggestions" 
						:key="index"
						class="suggestion-item"
					>
						<text class="suggestion-icon">•</text>
						<text class="suggestion-text">{{ suggestion }}</text>
					</view>
				</view>

				<button class="generate-path-btn" @click="generatePath">生成学习路径</button>
			</view>
		</scroll-view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				testStarted: false,
				testCompleted: false,
				currentIndex: 0,
				selectedAnswer: '',
				testQuestions: [
					{
						category: '词汇',
						question: 'Choose the word that best completes the sentence: The meeting was very _____, and everyone was engaged.',
						options: ['boring', 'productive', 'confusing', 'difficult']
					},
					{
						category: '语法',
						question: 'Which sentence is correct?',
						options: [
							'If I was you, I would study harder.',
							'If I were you, I would study harder.',
							'If I am you, I would study harder.',
							'If I be you, I would study harder.'
						]
					},
					{
						category: '阅读',
						question: 'Read the passage: "The company has seen a significant increase in revenue this quarter." What does "significant" mean?',
						options: ['small', 'important', 'negative', 'temporary']
					},
					{
						category: '词汇',
						question: 'What is the synonym of "enormous"?',
						options: ['tiny', 'huge', 'medium', 'average']
					},
					{
						category: '语法',
						question: 'Choose the correct form: She _____ to the library every week.',
						options: ['go', 'goes', 'went', 'going']
					}
				],
				testResult: {
					level: 'B1 Intermediate',
					description: '你具备基础的英语交流能力，可以处理日常话题和简单的学术内容。',
					suggestions: [
						'适合进阶：学术阅读',
						'写作结构需要重点提升',
						'建议加强口语流利度训练',
						'可以开始学习更复杂的语法结构'
					]
				}
			}
		},
		computed: {
			currentQuestion() {
				return this.testQuestions[this.currentIndex]
			},
			progress() {
				return ((this.currentIndex + 1) / this.testQuestions.length) * 100
			}
		},
		methods: {
			startTest() {
				this.testStarted = true
			},
			selectAnswer(option) {
				this.selectedAnswer = option
			},
			nextQuestion() {
				if (!this.selectedAnswer) return

				if (this.currentIndex < this.testQuestions.length - 1) {
					this.currentIndex++
					this.selectedAnswer = ''
				} else {
					// 完成测试
					this.completeTest()
				}
			},
			completeTest() {
				this.testCompleted = true
				// 保存测试结果到本地存储
				uni.setStorageSync('testResult', this.testResult)
				uni.setStorageSync('testCompleted', true)
			},
			generatePath() {
				uni.navigateTo({
					url: '/pages/international/path'
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

	.intro-section {
		background-color: #FFFFFF;
		border-radius: 24rpx;
		padding: 60rpx 40rpx;
		text-align: center;
		box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
	}

	.intro-text {
		display: block;
		font-size: 28rpx;
		color: #666;
		line-height: 1.8;
		margin-bottom: 24rpx;
	}

	.start-test-btn {
		background-color: #2F5D62;
		color: #FFFFFF;
		border: none;
		border-radius: 50rpx;
		padding: 24rpx 80rpx;
		font-size: 32rpx;
		margin-top: 40rpx;
		box-shadow: 0 4rpx 12rpx rgba(47, 93, 98, 0.2);
	}

	.test-card {
		background-color: #FFFFFF;
		border-radius: 24rpx;
		padding: 48rpx 40rpx;
		box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
	}

	.test-header {
		margin-bottom: 40rpx;
	}

	.question-number {
		display: block;
		font-size: 26rpx;
		color: #999;
		margin-bottom: 20rpx;
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

	.question-section {
		margin-bottom: 40rpx;
	}

	.question-type-label {
		display: block;
		font-size: 24rpx;
		color: #2F5D62;
		background-color: #F0F7F8;
		padding: 8rpx 16rpx;
		border-radius: 8rpx;
		margin-bottom: 24rpx;
		width: fit-content;
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

	.test-footer {
		display: flex;
		justify-content: center;
		padding-top: 32rpx;
		border-top: 1rpx solid #F0F0F0;
	}

	.next-btn {
		background-color: #2F5D62;
		color: #FFFFFF;
		border: none;
		border-radius: 50rpx;
		padding: 24rpx 80rpx;
		font-size: 32rpx;
		box-shadow: 0 4rpx 12rpx rgba(47, 93, 98, 0.2);
	}

	.next-btn:disabled {
		background-color: #E0E0E0;
		color: #B0B0B0;
		box-shadow: none;
	}

	.result-card {
		background-color: #FFFFFF;
		border-radius: 24rpx;
		padding: 60rpx 40rpx;
		box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
		animation: slideIn 0.5s ease;
	}

	@keyframes slideIn {
		from {
			opacity: 0;
			transform: translateY(20rpx);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.result-header {
		text-align: center;
		margin-bottom: 48rpx;
		padding-bottom: 40rpx;
		border-bottom: 1rpx solid #F0F0F0;
	}

	.result-title {
		display: block;
		font-size: 28rpx;
		color: #999;
		margin-bottom: 16rpx;
	}

	.result-level {
		display: block;
		font-size: 48rpx;
		font-weight: 500;
		color: #2F5D62;
		margin-bottom: 16rpx;
	}

	.result-desc {
		display: block;
		font-size: 26rpx;
		color: #666;
		line-height: 1.6;
	}

	.suggestions-section {
		margin-bottom: 48rpx;
	}

	.suggestions-title {
		display: block;
		font-size: 32rpx;
		font-weight: 500;
		color: #2F5D62;
		margin-bottom: 24rpx;
	}

	.suggestion-item {
		display: flex;
		align-items: flex-start;
		margin-bottom: 20rpx;
	}

	.suggestion-icon {
		font-size: 32rpx;
		color: #2F5D62;
		margin-right: 16rpx;
	}

	.suggestion-text {
		flex: 1;
		font-size: 28rpx;
		color: #666;
		line-height: 1.6;
	}

	.generate-path-btn {
		width: 100%;
		background-color: #2F5D62;
		color: #FFFFFF;
		border: none;
		border-radius: 50rpx;
		padding: 24rpx;
		font-size: 32rpx;
		box-shadow: 0 4rpx 12rpx rgba(47, 93, 98, 0.2);
	}
</style>

