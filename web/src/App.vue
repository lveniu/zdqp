<template>
  <div id="app">
    <el-container style="height: 100vh">
      <!-- 顶部导航 -->
      <el-header style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 0">
        <div style="display: flex; align-items: center; height: 100%; padding: 0 20px;">
          <h2 style="margin: 0; font-size: 20px;">🎯 整点抢券</h2>
          <el-button
            type="primary"
            size="small"
            @click="showAddUserDialog = true"
            style="margin-left: auto"
            plain
          >
            + 添加账号
          </el-button>
        </div>
      </el-header>

      <!-- 用户标签栏 -->
      <div style="padding: 10px 20px; background: #f5f7fa; border-bottom: 1px solid #e4e7ed">
        <el-space :size="10" wrap>
          <el-card
            v-for="user in users"
            :key="user.id"
            :class="['user-card', { 'active': activeUserId === user.id }]"
            @click="selectUser(user)"
            style="cursor: pointer; width: 200px"
            :body-style="{ padding: '15px' }"
          >
            <div class="user-card-header">
              <div class="user-name">{{ user.name }}</div>
              <el-button
                type="danger"
                :icon="Close"
                circle
                size="small"
                @click.stop="removeUser(user)"
                style="width: 20px; height: 20px; min-height: 20px"
              />
            </div>
            <div class="user-info">
              <div class="user-id">ID: {{ user.status.user_id || '加载中...' }}</div>
              <div class="user-points">积分: {{ user.status.current_points }}</div>
            </div>
            <div class="user-status">
              <el-tag :type="user.status.today_checkin ? 'success' : 'info'" size="small">
                {{ user.status.today_checkin ? '✓ 已打卡' : '未打卡' }}
              </el-tag>
              <el-tag :type="canUserGrab(user) ? 'success' : 'info'" size="small">
                {{ user.status.today_grab_count > 0 ? '✓ 已抢券' : '未抢券' }}
              </el-tag>
            </div>
          </el-card>

          <el-card
            v-if="users.length === 0"
            style="width: 200px; text-align: center; opacity: 0.6"
            :body-style="{ padding: '30px' }"
          >
            <div style="color: #909399">暂无账号</div>
            <el-button type="primary" size="small" @click="showAddUserDialog = true" style="margin-top: 10px">
              添加账号
            </el-button>
          </el-card>
        </el-space>
      </div>

      <!-- 主内容区 -->
      <el-main v-if="activeUser" style="padding: 20px">
        <!-- 顶部状态卡片 -->
        <el-row :gutter="20" style="margin-bottom: 20px">
          <el-col :span="6">
            <el-card shadow="hover">
              <el-statistic title="当前积分" :value="activeUser.status.current_points">
                <template #suffix>
                  <span style="color: #67C23A">分</span>
                </template>
              </el-statistic>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover">
              <el-statistic title="今日状态">
                <template #default>
                  <el-space>
                    <el-tag :type="activeUser.status.today_checkin ? 'success' : 'info'">
                      {{ activeUser.status.today_checkin ? '✓ 已打卡' : '未打卡' }}
                    </el-tag>
                    <el-tag :type="activeUser.status.today_grab_count > 0 ? 'success' : 'info'">
                      {{ activeUser.status.today_grab_count > 0 ? '✓ 已抢券' : '未抢券' }}
                    </el-tag>
                  </el-space>
                </template>
              </el-statistic>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover">
              <el-statistic title="累计抢券" :value="activeUser.status.total_grab_count">
                <template #suffix>
                  <span style="color: #E6A23C">次</span>
                </template>
              </el-statistic>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover">
              <el-statistic title="累计价值" :value="activeUser.status.total_grab_value" :precision="2">
                <template #prefix>
                  <span>¥</span>
                </template>
              </el-statistic>
            </el-card>
          </el-col>
        </el-row>

        <!-- 抢券限制提示 -->
        <el-alert
          v-if="!canUserGrab(activeUser) && getGrabLimitReason(activeUser)"
          :title="getGrabLimitReason(activeUser)"
          type="warning"
          :closable="false"
          style="margin-bottom: 20px"
        />

        <!-- 操作按钮区 -->
        <el-card shadow="hover" style="margin-bottom: 20px">
          <el-space :size="20">
            <el-button
              type="primary"
              :loading="activeUser.checkinLoading"
              :disabled="activeUser.status.today_checkin"
              @click="handleCheckin(activeUser)"
              size="large"
            >
              {{ activeUser.status.today_checkin ? '✓ 今日已打卡' : '📅 每日打卡' }}
            </el-button>

            <el-button
              type="success"
              :loading="activeUser.grabLoading"
              :disabled="!canUserGrab(activeUser)"
              @click="handleGrab(activeUser)"
              size="large"
            >
              🎁 抢5元券 (消耗100积分)
            </el-button>

            <el-button
              @click="refreshUserStatus(activeUser)"
              :loading="activeUser.statusLoading"
            >
              🔄 刷新状态
            </el-button>

            <el-button
              @click="showCookieDialog = true"
              type="warning"
              plain
            >
              🔑 修改Cookie
            </el-button>
          </el-space>
        </el-card>

        <!-- 详细信息折叠面板 -->
        <el-collapse v-model="activeCollapse" style="margin-bottom: 20px">
          <el-collapse-item title="📊 详细统计" name="stats">
            <el-descriptions :column="3" border>
              <el-descriptions-item label="当前积分">{{ activeUser.status.current_points }}</el-descriptions-item>
              <el-descriptions-item label="今日已抢">{{ activeUser.status.today_grab_count }}/1 次</el-descriptions-item>
              <el-descriptions-item label="本周已抢">{{ activeUser.status.week_grab_count }}/2 次</el-descriptions-item>
              <el-descriptions-item label="累计抢券">{{ activeUser.status.total_grab_count }} 次</el-descriptions-item>
              <el-descriptions-item label="累计价值">¥{{ activeUser.status.total_grab_value.toFixed(2) }}</el-descriptions-item>
              <el-descriptions-item label="连续打卡">{{ activeUser.status.consecutive_days }} 天</el-descriptions-item>
              <el-descriptions-item label="累计打卡">{{ activeUser.status.total_checkins }} 次</el-descriptions-item>
              <el-descriptions-item label="用户ID">{{ activeUser.status.user_id }}</el-descriptions-item>
              <el-descriptions-item label="抢券条件">
                <el-space>
                  <el-tag :type="activeUser.status.current_points >= 100 ? 'success' : 'danger'">积分≥100</el-tag>
                  <el-tag :type="activeUser.status.can_grab_today ? 'success' : 'info'">今日可抢</el-tag>
                  <el-tag :type="activeUser.status.can_grab_week ? 'success' : 'info'">本周可抢</el-tag>
                </el-space>
              </el-descriptions-item>
            </el-descriptions>
          </el-collapse-item>

          <el-collapse-item title="📅 打卡记录" name="checkin">
            <el-table :data="activeUser.checkinRecords" stripe v-loading="activeUser.recordsLoading">
              <el-table-column prop="date" label="日期" width="120" />
              <el-table-column prop="points" label="获得积分" width="100">
                <template #default="scope">
                  <el-tag type="success" size="small">+{{ scope.row.points }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="success" label="状态" width="80">
                <template #default="scope">
                  <el-tag :type="scope.row.success ? 'success' : 'danger'" size="small">
                    {{ scope.row.success ? '成功' : '失败' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="message" label="消息" />
              <el-table-column prop="created_at" label="时间" width="180">
                <template #default="scope">
                  {{ formatTime(scope.row.created_at) }}
                </template>
              </el-table-column>
            </el-table>
          </el-collapse-item>

          <el-collapse-item title="🎁 抢券记录" name="grab">
            <el-table :data="activeUser.grabRecords" stripe v-loading="activeUser.recordsLoading">
              <el-table-column prop="date" label="日期" width="120" />
              <el-table-column prop="success" label="结果" width="80">
                <template #default="scope">
                  <el-tag :type="scope.row.success ? 'success' : 'danger'" size="small">
                    {{ scope.row.success ? '成功' : '失败' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="coupon_value" label="券面值" width="100">
                <template #default="scope">
                  <span v-if="scope.row.success">¥{{ scope.row.coupon_value }}</span>
                  <span v-else>-</span>
                </template>
              </el-table-column>
              <el-table-column prop="coupon_id" label="券ID" width="200">
                <template #default="scope">
                  <el-text v-if="scope.row.coupon_id" size="small" type="info">
                    {{ scope.row.coupon_id }}
                  </el-text>
                </template>
              </el-table-column>
              <el-table-column prop="message" label="消息" />
              <el-table-column prop="created_at" label="时间" width="180">
                <template #default="scope">
                  {{ formatTime(scope.row.created_at) }}
                </template>
              </el-table-column>
            </el-table>
          </el-collapse-item>
        </el-collapse>
      </el-main>

      <!-- 空状态 -->
      <el-main v-else style="display: flex; align-items: center; justify-content: center">
        <el-empty description="请添加账号或选择一个账号">
          <el-button type="primary" @click="showAddUserDialog = true">添加账号</el-button>
        </el-empty>
      </el-main>
    </el-container>

    <!-- 添加用户对话框 -->
    <el-dialog
      v-model="showAddUserDialog"
      title="添加账号"
      width="500px"
    >
      <el-form :model="newUserForm" label-position="top">
        <el-form-item label="账号名称">
          <el-input v-model="newUserForm.name" placeholder="如：账号1、主号等" />
        </el-form-item>
        <el-form-item label="拼多多Cookie">
          <el-input
            v-model="newUserForm.cookies"
            type="textarea"
            :rows="6"
            placeholder="请粘贴拼多多Cookie"
          />
          <div style="margin-top: 5px; font-size: 12px; color: #909399;">
            从浏览器开发者工具中复制Cookie
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddUserDialog = false">取消</el-button>
        <el-button type="primary" @click="addUser" :loading="addUserLoading">
          添加并加载数据
        </el-button>
      </template>
    </el-dialog>

    <!-- 修改Cookie对话框 -->
    <el-dialog
      v-model="showCookieDialog"
      title="修改Cookie"
      width="500px"
    >
      <el-form :model="cookieEditForm" label-position="top">
        <el-form-item label="Cookie">
          <el-input
            v-model="cookieEditForm.cookies"
            type="textarea"
            :rows="6"
            placeholder="请粘贴新的拼多多Cookie"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCookieDialog = false">取消</el-button>
        <el-button type="primary" @click="saveCookie">保存并刷新</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Close } from '@element-plus/icons-vue'
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// 用户列表
const users = ref([])
const activeUserId = ref('')
const activeUser = computed(() => users.value.find(u => u.id === activeUserId.value))
const activeCollapse = ref(['stats'])

// 添加用户对话框
const showAddUserDialog = ref(false)
const newUserForm = ref({
  name: '',
  cookies: ''
})
const addUserLoading = ref(false)

// 修改Cookie对话框
const showCookieDialog = ref(false)
const cookieEditForm = ref({
  cookies: ''
})

// 检查用户是否可以抢券
const canUserGrab = (user) => {
  return user.status.can_grab_today &&
         user.status.can_grab_week &&
         user.status.current_points >= 100
}

// 获取抢券限制原因
const getGrabLimitReason = (user) => {
  if (!user.status.can_grab_today) {
    return '⚠️ 今天已抢1次，达到上限'
  }
  if (!user.status.can_grab_week) {
    return '⚠️ 本周已抢2次，达到上限'
  }
  if (user.status.current_points < 100) {
    return `⚠️ 积分不足，需要100积分，当前${user.status.current_points}`
  }
  return ''
}

// 选择用户
const selectUser = (user) => {
  activeUserId.value = user.id
  refreshUserStatus(user)
}

// 添加用户
const addUser = async () => {
  if (!newUserForm.value.name || !newUserForm.value.cookies) {
    ElMessage.warning('请填写完整信息')
    return
  }

  addUserLoading.value = true
  try {
    const userId = Date.now().toString()
    const user = {
      id: userId,
      name: newUserForm.value.name,
      cookies: newUserForm.value.cookies,
      userAgent: navigator.userAgent,
      status: {
        user_id: '',
        current_points: 0,
        can_grab_today: true,
        can_grab_week: true,
        today_grab_count: 0,
        week_grab_count: 0,
        total_grab_count: 0,
        total_grab_value: 0,
        today_checkin: false,
        consecutive_days: 0,
        total_checkins: 0
      },
      checkinRecords: [],
      grabRecords: [],
      statusLoading: false,
      checkinLoading: false,
      grabLoading: false,
      recordsLoading: false
    }

    // 加载用户状态
    await refreshUserStatus(user)

    users.value.push(user)
    activeUserId.value = userId

    // 保存到本地存储
    saveUsersToLocal()

    showAddUserDialog.value = false
    newUserForm.value = { name: '', cookies: '' }

    ElMessage.success('账号添加成功')
  } catch (error) {
    ElMessage.error('添加账号失败: ' + (error.message || ''))
  } finally {
    addUserLoading.value = false
  }
}

// 刷新用户状态
const refreshUserStatus = async (user) => {
  user.statusLoading = true
  try {
    const data = (await api.post('/status', {
      cookies: user.cookies,
      user_agent: user.userAgent
    })).data

    user.status = data

    // 加载记录
    await loadUserRecords(user)
  } catch (error) {
    ElMessage.error('获取状态失败')
    console.error(error)
  } finally {
    user.statusLoading = false
  }
}

// 加载用户记录
const loadUserRecords = async (user) => {
  user.recordsLoading = true
  try {
    const [checkinData, grabData] = await Promise.all([
      api.post('/records/checkin', {
        cookies: user.cookies,
        user_agent: user.userAgent
      }),
      api.post('/records/grab', {
        cookies: user.cookies,
        user_agent: user.userAgent
      })
    ])

    user.checkinRecords = checkinData.data || []
    user.grabRecords = grabData.data || []
  } catch (error) {
    console.error('获取记录失败:', error)
  } finally {
    user.recordsLoading = false
  }
}

// 打卡
const handleCheckin = async (user) => {
  try {
    await ElMessageBox.confirm('确认执行每日打卡？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })

    user.checkinLoading = true
    const result = (await api.post('/checkin', {
      cookies: user.cookies,
      user_agent: user.userAgent
    })).data

    if (result.success) {
      ElMessage.success(`打卡成功！获得 ${result.points_gained} 积分`)
    } else {
      ElMessage.warning(result.message)
    }

    await refreshUserStatus(user)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('打卡失败')
    }
  } finally {
    user.checkinLoading = false
  }
}

// 抢券
const handleGrab = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确认抢券？将消耗 100 积分\n` +
      `今日已抢：${user.status.today_grab_count}/1 次\n` +
      `本周已抢：${user.status.week_grab_count}/2 次`,
      '确认抢券',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    user.grabLoading = true
    const result = (await api.post('/grab', {
      cookies: user.cookies,
      user_agent: user.userAgent
    })).data

    if (result.success) {
      ElMessage.success(`抢券成功！券ID: ${result.coupon_id}`)
    } else {
      ElMessage.warning(result.message)
    }

    await refreshUserStatus(user)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('抢券失败')
    }
  } finally {
    user.grabLoading = false
  }
}

// 移除用户
const removeUser = (user) => {
  ElMessageBox.confirm(`确认移除账号 "${user.name}"？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    users.value = users.value.filter(u => u.id !== user.id)
    if (activeUserId.value === user.id && users.value.length > 0) {
      activeUserId.value = users.value[0].id
    }
    saveUsersToLocal()
    ElMessage.success('账号已移除')
  }).catch(() => {})
}

// 保存Cookie
const saveCookie = () => {
  if (activeUser && cookieEditForm.value.cookies) {
    activeUser.cookies = cookieEditForm.value.cookies
    saveUsersToLocal()
    showCookieDialog.value = false
    refreshUserStatus(activeUser)
    ElMessage.success('Cookie已更新')
  }
}

// 保存到本地存储
const saveUsersToLocal = () => {
  const data = users.value.map(user => ({
    id: user.id,
    name: user.name,
    cookies: user.cookies,
    userAgent: user.userAgent
  }))
  localStorage.setItem('baibuti_users', JSON.stringify(data))
}

// 从本地存储加载
const loadUsersFromLocal = () => {
  const data = localStorage.getItem('baibuti_users')
  if (data) {
    try {
      const savedUsers = JSON.parse(data)
      savedUsers.forEach(savedUser => {
        const user = {
          ...savedUser,
          status: {
            user_id: '',
            current_points: 0,
            can_grab_today: true,
            can_grab_week: true,
            today_grab_count: 0,
            week_grab_count: 0,
            total_grab_count: 0,
            total_grab_value: 0,
            today_checkin: false,
            consecutive_days: 0,
            total_checkins: 0
          },
          checkinRecords: [],
          grabRecords: [],
          statusLoading: false,
          checkinLoading: false,
          grabLoading: false,
          recordsLoading: false
        }
        users.value.push(user)
      })

      if (users.value.length > 0) {
        activeUserId.value = users.value[0].id
        // 自动加载第一个用户
        refreshUserStatus(users.value[0])
      }
    } catch (error) {
      console.error('加载用户数据失败:', error)
    }
  }
}

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN')
}

let refreshTimer = null

onMounted(() => {
  loadUsersFromLocal()

  // 自动刷新所有用户状态
  refreshTimer = setInterval(() => {
    users.value.forEach(user => {
      refreshUserStatus(user)
    })
  }, 60000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
#app {
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

.user-card {
  transition: all 0.3s;
  border: 2px solid transparent;
}

.user-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.user-card.active {
  border-color: #409EFF;
  background: #ecf5ff;
}

.user-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.user-name {
  font-weight: bold;
  font-size: 16px;
  color: #303133;
}

.user-info {
  margin-bottom: 10px;
}

.user-id {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.user-points {
  font-size: 14px;
  color: #67C23A;
  font-weight: bold;
}

.user-status {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

:deep(.el-collapse-item__header) {
  font-weight: bold;
  font-size: 16px;
}

:deep(.el-card__body) {
  padding: 15px;
}
</style>
