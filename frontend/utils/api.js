/**
 * API请求工具
 */
const API_BASE_URL = 'http://127.0.0.1:8000/api/v1'

/**
 * 通用请求函数
 */
function request(url, method = 'GET', data = {}, header = {}) {
	return new Promise((resolve, reject) => {
		const fullUrl = API_BASE_URL + url
		console.log(`[API请求] ${method} ${fullUrl}`, data)
		
		uni.request({
			url: fullUrl,
			method: method,
			data: data,
			header: {
				'Content-Type': 'application/json',
				...header
			},
			timeout: 30000, // 30秒超时
			success: (res) => {
				console.log(`[API响应] ${method} ${fullUrl}`, res.statusCode, res.data)
				if (res.statusCode === 200 || res.statusCode === 201) {
					resolve(res.data)
				} else {
					// FastAPI错误响应格式: {detail: "错误信息"}
					reject({
						statusCode: res.statusCode,
						data: res.data,
						errMsg: res.errMsg || `请求失败: ${res.statusCode}`
					})
				}
			},
			fail: (err) => {
				console.error(`[API失败] ${method} ${fullUrl}`, err)
				// 提供更详细的错误信息
				let errorMsg = err.errMsg || '请求失败'
				if (err.errMsg) {
					if (err.errMsg.includes('timeout')) {
						errorMsg = '请求超时，请检查网络连接'
					} else if (err.errMsg.includes('fail') || err.errMsg.includes('connect')) {
						errorMsg = '无法连接到服务器，请确保后端服务已启动 (http://127.0.0.1:8000)'
					}
				}
				reject({
					...err,
					errMsg: errorMsg
				})
			}
		})
	})
}

/**
 * 带token的请求
 */
function requestWithToken(url, method = 'GET', data = {}) {
	const token = uni.getStorageSync('token')
	return request(url, method, data, {
		'Authorization': `Bearer ${token}`
	})
}

/**
 * 用户注册
 */
export function register(username, phone, password) {
	return request('/auth/register', 'POST', {
		username,
		phone,
		password
	})
}

/**
 * 用户登录
 */
export function login(username, password) {
	return request('/auth/login', 'POST', {
		username,
		password
	})
}

/**
 * 忘记密码 - 请求重置
 */
export function forgotPassword(email) {
	return request('/auth/forgot-password', 'POST', {
		email
	})
}

/**
 * 重置密码
 */
export function resetPassword(token, newPassword) {
	return request('/auth/reset-password', 'POST', {
		token,
		new_password: newPassword
	})
}

/**
 * 发送短信验证码
 */
export function sendSmsCode(phone, purpose = 'login') {
	return request('/auth/send-sms-code', 'POST', {
		phone,
		purpose
	})
}

/**
 * 短信验证码登录
 */
export function smsLogin(phone, code) {
	return request('/auth/sms-login', 'POST', {
		phone,
		code
	})
}

/**
 * 获取用户资料
 */
export function getProfile() {
	return requestWithToken('/profile/me', 'GET')
}

/**
 * 更新用户资料
 */
export function updateProfile(data) {
	return requestWithToken('/profile/me', 'PUT', data)
}

/**
 * 上传头像
 */
export function uploadAvatar(filePath) {
	return new Promise((resolve, reject) => {
		const token = uni.getStorageSync('token')
		uni.uploadFile({
			url: API_BASE_URL + '/profile/avatar',
			filePath: filePath,
			name: 'file',
			header: {
				'Authorization': `Bearer ${token}`
			},
			success: (res) => {
				try {
					const data = JSON.parse(res.data)
					if (res.statusCode === 200) {
						resolve(data)
					} else {
						reject({
							statusCode: res.statusCode,
							data: data,
							errMsg: data.detail || '上传失败'
						})
					}
				} catch (e) {
					reject({
						statusCode: res.statusCode,
						errMsg: '解析响应失败'
					})
				}
			},
			fail: (err) => {
				reject(err)
			}
		})
	})
}

/**
 * 获取学习统计
 */
export function getLearningStats() {
	return requestWithToken('/learning/stats', 'GET')
}

/**
 * 获取公立模式信息
 */
export function getPublicInfo() {
	return requestWithToken('/learning/public/info', 'GET')
}

/**
 * 获取国际模式信息
 */
export function getInternationalInfo() {
	return requestWithToken('/learning/international/info', 'GET')
}

/**
 * 获取年级列表
 */
export function getGrades() {
	return request('/public/grades', 'GET')
}

/**
 * 获取教材版本列表
 */
export function getVersions() {
	return request('/public/versions', 'GET')
}

/**
 * 获取单元列表
 */
export function getUnits(grade, version) {
	return request('/public/units', 'GET', { grade, version })
}

/**
 * 开始练习
 */
export function startPractice(grade, version, unit) {
	return requestWithToken('/public/practice/start', 'POST', {
		grade,
		version,
		unit
	})
}

/**
 * 获取练习题列表
 */
export function getPracticeQuestions(sessionId) {
	return requestWithToken('/public/practice/questions', 'GET', { session_id: sessionId })
}

/**
 * 提交答案
 */
export function submitAnswer(sessionId, questionId, answer) {
	return requestWithToken('/public/practice/submit', 'POST', {
		session_id: sessionId,
		question_id: questionId,
		answer
	})
}

/**
 * 结束练习
 */
export function endPractice(sessionId) {
	return requestWithToken('/public/practice/end', 'POST', {
		session_id: sessionId
	})
}

/**
 * 获取测试题目（支持游览模式，token可选）
 */
export function getTestQuestions() {
	const token = uni.getStorageSync('token')
	if (token) {
		// 已登录：使用token
		return requestWithToken('/international/test/questions', 'GET')
	} else {
		// 游览模式：不使用token
		return request('/international/test/questions', 'GET')
	}
}

/**
 * 提交测试答案（支持游览模式，token可选）
 */
export function submitTest(answers) {
	const token = uni.getStorageSync('token')
	if (token) {
		// 已登录：使用token
		return requestWithToken('/international/test/submit', 'POST', {
			answers
		})
	} else {
		// 游览模式：不使用token（但测试结果不保存到数据库）
		return request('/international/test/submit', 'POST', {
			answers
		})
	}
}

/**
 * 获取学习路径模块
 */
export function getLearningModules(targetLevel) {
	return requestWithToken('/international/path/modules', 'GET', { target_level: targetLevel })
}

/**
 * 切换学习模块状态
 */
export function toggleLearningModule(moduleId) {
	return requestWithToken(`/international/path/modules/${moduleId}/toggle`, 'POST')
}

/**
 * AI教练对话（支持游览模式，token可选）
 */
export function chatWithCoach(message) {
	const token = uni.getStorageSync('token')
	if (token) {
		// 已登录：使用token
		return requestWithToken('/international/coach/chat', 'POST', {
			message
		})
	} else {
		// 游览模式：不使用token
		return request('/international/coach/chat', 'POST', {
			message
		})
	}
}

/**
 * 获取学习路径配置
 */
export function getPathConfig() {
	return requestWithToken('/international/path/config', 'GET')
}

/**
 * 获取错题本列表
 */
export function getWrongBookList(page = 1, pageSize = 20) {
	return requestWithToken('/wrongbook/list', 'GET', { page, page_size: pageSize })
}

/**
 * 添加错题
 */
export function addWrongQuestion(data) {
	return requestWithToken('/wrongbook/add', 'POST', data)
}

/**
 * 删除错题
 */
export function deleteWrongQuestion(wrongId) {
	return requestWithToken(`/wrongbook/${wrongId}`, 'DELETE')
}

/**
 * 生成错题复习题目
 */
export function reviewWrongQuestions() {
	return requestWithToken('/wrongbook/review', 'POST')
}

/**
 * 获取生词本列表
 */
export function getWordBookList(page = 1, pageSize = 20) {
	return requestWithToken('/wordbook/list', 'GET', { page, page_size: pageSize })
}

/**
 * 添加生词
 */
export function addWord(word, meaning, example) {
	return requestWithToken('/wordbook/add', 'POST', {
		word,
		meaning,
		example
	})
}

/**
 * 删除生词
 */
export function deleteWord(wordId) {
	return requestWithToken(`/wordbook/${wordId}`, 'DELETE')
}

/**
 * 获取生词复习列表
 */
export function getReviewWords() {
	return requestWithToken('/wordbook/review', 'GET')
}

export default {
	register,
	login,
	forgotPassword,
	resetPassword,
	sendSmsCode,
	smsLogin,
	getProfile,
	updateProfile,
	uploadAvatar,
	getLearningStats,
	getPublicInfo,
	getInternationalInfo,
	getGrades,
	getVersions,
	getUnits,
	startPractice,
	getPracticeQuestions,
	submitAnswer,
	endPractice,
	getTestQuestions,
	submitTest,
	getLearningModules,
	toggleLearningModule,
	chatWithCoach,
	getPathConfig,
	getWrongBookList,
	addWrongQuestion,
	deleteWrongQuestion,
	reviewWrongQuestions,
	getWordBookList,
	addWord,
	deleteWord,
	getReviewWords,
	request,
	requestWithToken
}

