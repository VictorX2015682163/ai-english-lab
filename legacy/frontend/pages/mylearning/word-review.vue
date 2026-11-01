<template>
	<view class="container">
		<view class="content">
			<!-- 顶部进度 -->
			<view class="progress-section">
				<text class="progress-text">{{ currentIndex + 1 }} / {{ wordList.length }}</text>
				<view class="progress-bar">
					<view class="progress-fill" :style="{ width: progress + '%' }"></view>
				</view>
			</view>

			<!-- 单词卡片 -->
			<view class="word-card" v-if="currentWord">
				<view class="card-front" v-if="!showAnswer">
					<text class="word-text">{{ currentWord.word }}</text>
					<text class="word-phonetic" v-if="currentWord.phonetic">[{{ currentWord.phonetic }}]</text>
					<button class="show-btn" @click="showAnswer = true">显示答案</button>
				</view>
				<view class="card-back" v-else>
					<text class="word-text">{{ currentWord.word }}</text>
					<text class="word-phonetic" v-if="currentWord.phonetic">[{{ currentWord.phonetic }}]</text>
					<text class="word-meaning">{{ currentWord.meaning }}</text>
					<text class="word-example" v-if="currentWord.example">{{ currentWord.example }}</text>
				</view>
			</view>

			<!-- 操作按钮 -->
			<view class="action-buttons" v-if="showAnswer">
				<button class="action-btn wrong-btn" @click="markWrong">不认识</button>
				<button class="action-btn right-btn" @click="markRight">认识</button>
			</view>

			<!-- 完成提示 -->
			<view class="complete-section" v-if="completed">
				<text class="complete-icon">🎉</text>
				<text class="complete-title">复习完成！</text>
				<text class="complete-desc">本次复习了 {{ wordList.length }} 个生词</text>
				<button class="complete-btn" @click="goBack">返回生词本</button>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				wordList: [],
				currentIndex: 0,
				showAnswer: false,
				completed: false,
				reviewedWords: []
			}
		},
		computed: {
			currentWord() {
				return this.wordList[this.currentIndex] || null
			},
			progress() {
				return this.wordList.length > 0 ? ((this.currentIndex + 1) / this.wordList.length) * 100 : 0
			}
		},
		onLoad() {
			this.loadWords()
		},
		methods: {
			loadWords() {
				const words = uni.getStorageSync('wordBook') || []
				// 过滤无效数据
				const validWords = words.filter(w => w && w.word && w.meaning)
				if (validWords.length === 0) {
					uni.showToast({
						title: '生词本为空',
						icon: 'none'
					})
					setTimeout(() => {
						uni.navigateBack()
					}, 1500)
					return
				}
				// 打乱顺序
				this.wordList = this.shuffleArray([...validWords])
			},
			shuffleArray(array) {
				const newArray = [...array]
				for (let i = newArray.length - 1; i > 0; i--) {
					const j = Math.floor(Math.random() * (i + 1));
					[newArray[i], newArray[j]] = [newArray[j], newArray[i]]
				}
				return newArray
			},
			markRight() {
				if (!this.currentWord || !this.currentWord.word) return
				this.reviewedWords.push({
					word: this.currentWord.word,
					correct: true
				})
				this.nextWord()
			},
			markWrong() {
				if (!this.currentWord || !this.currentWord.word) return
				this.reviewedWords.push({
					word: this.currentWord.word,
					correct: false
				})
				// 不认识的单词会再次加入列表末尾
				this.wordList.push({...this.currentWord})
				this.nextWord()
			},
			nextWord() {
				this.currentIndex++
				this.showAnswer = false

				if (this.currentIndex >= this.wordList.length) {
					this.completed = true
					this.saveReviewResult()
				}
			},
			saveReviewResult() {
				// 更新复习记录
				const words = uni.getStorageSync('wordBook') || []
				this.reviewedWords.forEach(review => {
					if (!review || !review.word) return
					const word = words.find(w => w && w.word && w.word === review.word)
					if (word) {
						word.reviewCount = (word.reviewCount || 0) + 1
						word.lastReviewAt = new Date().toISOString()
					}
				})
				uni.setStorageSync('wordBook', words)
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
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.progress-section {
		width: 100%;
		margin-bottom: 60rpx;
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

	.word-card {
		width: 100%;
		background-color: #FFFFFF;
		border-radius: 24rpx;
		padding: 80rpx 40rpx;
		box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
		min-height: 400rpx;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		margin-bottom: 60rpx;
	}

	.card-front,
	.card-back {
		width: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
	}

	.word-text {
		font-size: 64rpx;
		font-weight: 500;
		color: #2F5D62;
		margin-bottom: 24rpx;
	}

	.word-phonetic {
		font-size: 32rpx;
		color: #999;
		margin-bottom: 40rpx;
	}

	.show-btn {
		background-color: #2F5D62;
		color: #FFFFFF;
		border: none;
		border-radius: 50rpx;
		padding: 20rpx 48rpx;
		font-size: 28rpx;
		margin-top: 40rpx;
	}

	.word-meaning {
		font-size: 36rpx;
		color: #333;
		margin-bottom: 32rpx;
		line-height: 1.6;
	}

	.word-example {
		font-size: 28rpx;
		color: #666;
		font-style: italic;
		line-height: 1.6;
		padding: 24rpx;
		background-color: #F5F5F5;
		border-radius: 12rpx;
		width: 100%;
		box-sizing: border-box;
	}

	.action-buttons {
		display: flex;
		gap: 24rpx;
		width: 100%;
	}

	.action-btn {
		flex: 1;
		padding: 28rpx;
		border-radius: 50rpx;
		font-size: 32rpx;
		border: none;
	}

	.wrong-btn {
		background-color: #FFE5E5;
		color: #FF5252;
	}

	.right-btn {
		background-color: #E8F5E9;
		color: #4CAF50;
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
		margin-bottom: 60rpx;
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

