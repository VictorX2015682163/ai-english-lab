<template>
	<view class="container">
		<view class="content">
			<!-- 顶部标题栏 -->
			<view class="header-section">
				<text class="main-title">生词本</text>
				<text class="sub-title">共 {{ wordList.length }} 个生词</text>
			</view>

			<!-- 添加生词按钮 -->
			<view class="add-word-section">
				<button class="add-btn" @click="showAddModal">+ 添加生词</button>
			</view>

			<!-- 生词列表 -->
			<view class="word-list" v-if="wordList.length > 0">
				<view 
					v-for="(word, index) in wordList" 
					:key="word.id || index"
					class="word-item"
				>
					<view class="word-content">
						<view class="word-header">
							<text class="word-text">{{ word.word }}</text>
							<text class="word-phonetic" v-if="word.phonetic">[{{ word.phonetic }}]</text>
						</view>
						<text class="word-meaning">{{ word.meaning }}</text>
						<text class="word-example" v-if="word.example">{{ word.example }}</text>
						<text class="word-time">添加时间：{{ formatTime(word.addedAt) }}</text>
					</view>
					<view class="word-actions">
						<button class="action-btn delete-btn" @click="deleteWord(word)">删除</button>
					</view>
				</view>
			</view>

			<!-- 空状态 -->
			<view class="empty-state" v-else>
				<text class="empty-icon">📚</text>
				<text class="empty-text">还没有生词</text>
				<text class="empty-desc">点击上方按钮添加生词</text>
			</view>
		</view>

		<!-- 添加生词弹窗 -->
		<view class="modal-overlay" v-if="showModal" @click="hideAddModal">
			<view class="modal-content" @click.stop>
				<view class="modal-header">
					<text class="modal-title">添加生词</text>
					<text class="modal-close" @click="hideAddModal">×</text>
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
					<button class="modal-btn cancel-btn" @click="hideAddModal">取消</button>
					<button class="modal-btn confirm-btn" @click="addWord">确定</button>
				</view>
			</view>
		</view>
	</view>
</template>

<script>
	export default {
		data() {
			return {
				wordList: [],
				showModal: false,
				newWord: {
					word: '',
					phonetic: '',
					meaning: '',
					example: ''
				}
			}
		},
		onLoad() {
			this.loadWords()
		},
		onShow() {
			this.loadWords()
		},
		methods: {
			loadWords() {
				const words = uni.getStorageSync('wordBook') || []
				// 过滤无效数据
				this.wordList = words.filter(w => w && w.word && w.meaning)
			},
			showAddModal() {
				this.showModal = true
				this.newWord = {
					word: '',
					phonetic: '',
					meaning: '',
					example: ''
				}
			},
			hideAddModal() {
				this.showModal = false
			},
			addWord() {
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
				
				words.unshift(word) // 添加到开头
				uni.setStorageSync('wordBook', words)

				this.loadWords()
				this.hideAddModal()

				uni.showToast({
					title: '添加成功',
					icon: 'success'
				})
			},
			deleteWord(word) {
				uni.showModal({
					title: '确认删除',
					content: '确定要删除这个生词吗？',
					success: (res) => {
						if (res.confirm) {
							const words = uni.getStorageSync('wordBook') || []
							// 通过 id 找到要删除的项
							const index = words.findIndex(w => w.id === word.id)
							if (index !== -1) {
								words.splice(index, 1)
								uni.setStorageSync('wordBook', words)
								this.loadWords()
								uni.showToast({
									title: '已删除',
									icon: 'success'
								})
							}
						}
					}
				})
			},
			formatTime(timeStr) {
				if (!timeStr) return ''
				const date = new Date(timeStr)
				const now = new Date()
				const diff = now - date
				const days = Math.floor(diff / (1000 * 60 * 60 * 24))
				
				if (days === 0) {
					const hours = Math.floor(diff / (1000 * 60 * 60))
					if (hours === 0) {
						const minutes = Math.floor(diff / (1000 * 60))
						return minutes <= 0 ? '刚刚' : `${minutes}分钟前`
					}
					return `${hours}小时前`
				} else if (days === 1) {
					return '昨天'
				} else if (days < 7) {
					return `${days}天前`
				} else {
					return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
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
		padding: 40rpx;
		width: 100%;
		box-sizing: border-box;
	}

	.header-section {
		text-align: center;
		margin-bottom: 40rpx;
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

	.add-word-section {
		margin-bottom: 32rpx;
	}

	.add-btn {
		width: 100%;
		background-color: #2F5D62;
		color: #FFFFFF;
		border: none;
		border-radius: 50rpx;
		padding: 24rpx;
		font-size: 28rpx;
		box-shadow: 0 4rpx 12rpx rgba(47, 93, 98, 0.2);
	}

	.word-list {
		display: flex;
		flex-direction: column;
		gap: 24rpx;
	}

	.word-item {
		background-color: #FFFFFF;
		border-radius: 24rpx;
		padding: 32rpx;
		box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
	}

	.word-content {
		flex: 1;
	}

	.word-header {
		display: flex;
		align-items: baseline;
		margin-bottom: 12rpx;
	}

	.word-text {
		font-size: 36rpx;
		font-weight: 500;
		color: #2F5D62;
		margin-right: 16rpx;
	}

	.word-phonetic {
		font-size: 24rpx;
		color: #999;
	}

	.word-meaning {
		display: block;
		font-size: 28rpx;
		color: #333;
		margin-bottom: 12rpx;
		line-height: 1.6;
	}

	.word-example {
		display: block;
		font-size: 26rpx;
		color: #666;
		font-style: italic;
		margin-bottom: 12rpx;
		line-height: 1.6;
	}

	.word-time {
		display: block;
		font-size: 24rpx;
		color: #999;
	}

	.word-actions {
		display: flex;
		flex-direction: column;
		gap: 12rpx;
		margin-left: 24rpx;
	}

	.action-btn {
		padding: 12rpx 24rpx;
		border-radius: 20rpx;
		font-size: 24rpx;
		border: none;
	}

	.delete-btn {
		background-color: #FFE5E5;
		color: #FF5252;
	}

	.empty-state {
		text-align: center;
		padding: 120rpx 40rpx;
	}

	.empty-icon {
		display: block;
		font-size: 120rpx;
		margin-bottom: 32rpx;
	}

	.empty-text {
		display: block;
		font-size: 32rpx;
		color: #666;
		margin-bottom: 16rpx;
	}

	.empty-desc {
		display: block;
		font-size: 26rpx;
		color: #999;
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

