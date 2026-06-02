<template>
  <div>
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px">
      <h1 style="font-size:20px">👥 用户管理</h1>
      <input v-model="keyword" placeholder="搜索邮箱/姓名..." style="width:240px" @input="debouncedSearch" />
    </div>

    <div class="card">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>邮箱</th>
            <th>姓名</th>
            <th>状态</th>
            <th>注册时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td>{{ u.id }}</td>
            <td>{{ u.email }}</td>
            <td>{{ u.first_name }} {{ u.last_name }}</td>
            <td><span :class="['badge', u.is_active ? 'badge-green' : 'badge-red']">{{ u.is_active ? '正常' : '禁用' }}</span></td>
            <td>{{ formatDate(u.created_at) }}</td>
            <td>
              <button :class="u.is_active ? 'btn-danger btn-sm' : 'btn-primary btn-sm'" @click="toggleActive(u)">
                {{ u.is_active ? '禁用' : '启用' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div class="pagination" v-if="total > perPage">
        <button class="btn-sm" :disabled="page <= 1" @click="page--; loadUsers()">上一页</button>
        <span>{{ page }} / {{ Math.ceil(total / perPage) }}</span>
        <button class="btn-sm" :disabled="page >= Math.ceil(total / perPage)" @click="page++; loadUsers()">下一页</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { userApi } from '../api'

const users = ref([])
const total = ref(0)
const page = ref(1)
const perPage = 20
const keyword = ref('')
let searchTimer = null

function formatDate(str) {
  if (!str) return ''
  return new Date(str).toLocaleString('zh-CN')
}

async function loadUsers() {
  try {
    const data = await userApi.list({ page: page.value, per_page: perPage, keyword: keyword.value || undefined })
    users.value = data.items
    total.value = data.total
  } catch (e) { console.error(e) }
}

function debouncedSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { page.value = 1; loadUsers() }, 300)
}

async function toggleActive(user) {
  try {
    const data = await userApi.toggleActive(user.id)
    user.is_active = data.is_active
  } catch (e) { console.error(e) }
}

onMounted(loadUsers)
</script>

<style scoped>
.pagination { display: flex; align-items: center; justify-content: center; gap: 16px; padding: 16px 0 0; font-size: 13px; color: #6b7280; }
</style>
