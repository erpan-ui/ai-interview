<template>
  <div class="container">
    <div class="profile-page">
      <h2 style="margin-bottom:24px">👤 个人中心</h2>

      <div class="card avatar-section">
        <div class="avatar-wrapper" @click="$refs.avatarInput.click()">
          <img v-if="profile.avatar" :src="avatarUrl" class="avatar-img" alt="avatar" />
          <div v-else class="avatar-placeholder">{{ initials }}</div>
          <div class="avatar-overlay">📷</div>
          <input ref="avatarInput" type="file" accept="image/*" @change="handleAvatarChange" hidden />
        </div>
        <div class="avatar-info">
          <p class="avatar-name">{{ profile.first_name || '' }} {{ profile.last_name || '' }}</p>
          <p class="avatar-email">{{ profile.email }}</p>
        </div>
      </div>

      <div class="card" style="margin-top:16px">
        <h3 style="margin-bottom:16px">基本信息</h3>
        <div class="form-row">
          <div class="form-group">
            <label>姓</label>
            <input v-model="form.last_name" placeholder="姓" />
          </div>
          <div class="form-group">
            <label>名</label>
            <input v-model="form.first_name" placeholder="名" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>性别</label>
            <select v-model="form.gender">
              <option value="">未设置</option>
              <option value="male">男</option>
              <option value="female">女</option>
            </select>
          </div>
          <div class="form-group">
            <label>手机号</label>
            <input v-model="form.phone" placeholder="手机号" />
          </div>
        </div>
        <div class="form-group">
          <label>学校</label>
          <input v-model="form.university" placeholder="学校名称" />
        </div>
        <div class="form-group">
          <label>求职目标</label>
          <input v-model="form.career_goal" placeholder="例如：Python后端开发工程师" />
        </div>
        <div class="form-group">
          <label>所在城市</label>
          <input v-model="form.location" placeholder="例如：上海" />
        </div>
        <p v-if="profileMsg" :class="profileMsg.startsWith('✅') ? 'success-msg' : 'error'">{{ profileMsg }}</p>
        <button class="btn-primary" style="width:100%;margin-top:8px" @click="handleSaveProfile" :disabled="saving">
          {{ saving ? '保存中...' : '保存信息' }}
        </button>
      </div>

      <div class="card" style="margin-top:16px">
        <h3 style="margin-bottom:16px">🔒 修改密码</h3>
        <div class="form-group">
          <label>当前密码</label>
          <input v-model="pwForm.old_password" type="password" placeholder="输入当前密码" />
        </div>
        <div class="form-group">
          <label>新密码</label>
          <input v-model="pwForm.new_password" type="password" placeholder="至少6位" />
        </div>
        <div class="form-group">
          <label>确认新密码</label>
          <input v-model="pwForm.confirm_password" type="password" placeholder="再次输入新密码" />
        </div>
        <p v-if="pwMsg" :class="pwMsg.startsWith('✅') ? 'success-msg' : 'error'">{{ pwMsg }}</p>
        <button class="btn-primary" style="width:100%;margin-top:8px" @click="handleChangePassword" :disabled="changingPw">
          {{ changingPw ? '修改中...' : '修改密码' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getProfile, updateProfile, uploadAvatar, changePassword } from '../api/user'

const profile = ref({})
const form = ref({ first_name: '', last_name: '', gender: '', phone: '', university: '', career_goal: '', location: '' })
const pwForm = ref({ old_password: '', new_password: '', confirm_password: '' })
const saving = ref(false)
const changingPw = ref(false)
const profileMsg = ref('')
const pwMsg = ref('')

const avatarUrl = computed(() => {
  if (!profile.value.avatar) return ''
  if (profile.value.avatar.startsWith('http')) return profile.value.avatar
  return profile.value.avatar
})

const initials = computed(() => {
  const f = profile.value.first_name || ''
  const l = profile.value.last_name || ''
  return (l.charAt(0) + f.charAt(0)).toUpperCase() || '👤'
})

onMounted(async () => {
  try {
    const data = await getProfile()
    profile.value = data
    form.value = {
      first_name: data.first_name || '',
      last_name: data.last_name || '',
      gender: data.gender || '',
      phone: data.phone || '',
      university: data.university || '',
      career_goal: data.career_goal || '',
      location: data.location || ''
    }
  } catch (e) {
    console.error(e)
  }
})

async function handleAvatarChange(e) {
  const file = e.target.files[0]
  if (!file) return
  try {
    const data = await uploadAvatar(file)
    profile.value.avatar = data.avatar
  } catch (e) {
    alert('头像上传失败: ' + e.message)
  }
}

async function handleSaveProfile() {
  profileMsg.value = ''
  saving.value = true
  try {
    await updateProfile(form.value)
    profile.value = { ...profile.value, ...form.value }
    profileMsg.value = '✅ 保存成功'
  } catch (e) {
    profileMsg.value = e.message
  } finally {
    saving.value = false
  }
}

async function handleChangePassword() {
  pwMsg.value = ''
  if (pwForm.value.new_password !== pwForm.value.confirm_password) {
    pwMsg.value = '两次密码不一致'
    return
  }
  if (pwForm.value.new_password.length < 6) {
    pwMsg.value = '新密码至少6位'
    return
  }
  changingPw.value = true
  try {
    await changePassword(pwForm.value.old_password, pwForm.value.new_password)
    pwMsg.value = '✅ 密码修改成功'
    pwForm.value = { old_password: '', new_password: '', confirm_password: '' }
  } catch (e) {
    pwMsg.value = e.message
  } finally {
    changingPw.value = false
  }
}
</script>

<style scoped>
.profile-page { max-width: 560px; margin: 20px auto; }
.avatar-section { display: flex; align-items: center; gap: 20px; }
.avatar-wrapper {
  width: 80px; height: 80px; border-radius: 50%; position: relative;
  cursor: pointer; overflow: hidden; flex-shrink: 0;
}
.avatar-img { width: 100%; height: 100%; object-fit: cover; }
.avatar-placeholder {
  width: 100%; height: 100%; background: linear-gradient(135deg, #4f46e5, #7c3aed);
  color: white; display: flex; align-items: center; justify-content: center;
  font-size: 24px; font-weight: 700;
}
.avatar-overlay {
  position: absolute; inset: 0; background: rgba(0,0,0,0.4);
  display: flex; align-items: center; justify-content: center;
  font-size: 24px; opacity: 0; transition: opacity 0.2s;
}
.avatar-wrapper:hover .avatar-overlay { opacity: 1; }
.avatar-name { font-size: 18px; font-weight: 600; }
.avatar-email { font-size: 13px; color: #6b7280; margin-top: 4px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.form-group { margin-bottom: 14px; }
.form-group label { display: block; margin-bottom: 6px; font-size: 13px; font-weight: 500; color: #374151; }
.error { color: #ef4444; font-size: 13px; margin-top: 8px; }
.success-msg { color: #059669; font-size: 13px; margin-top: 8px; }
</style>
