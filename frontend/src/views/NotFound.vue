<template>
  <div class="not-found">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <h1>页面未找到</h1>
      <p>抱歉，您访问的页面不存在</p>
      <div class="actions">
        <el-button type="primary" @click="$router.push('/')">
          回到首页
        </el-button>
        <el-button @click="$router.go(-1)">
          返回上页
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
// 404页面组件
</script>

<style lang="scss" scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--bg-light);
}

.not-found-content {
  text-align: center;
  
  .error-code {
    font-size: 8rem;
    font-weight: bold;
    color: var(--primary-color);
    margin-bottom: 20px;
  }
  
  h1 {
    font-size: 2rem;
    color: var(--text-primary);
    margin-bottom: 10px;
  }
  
  p {
    color: var(--text-secondary);
    margin-bottom: 30px;
    font-size: 1.1rem;
  }
  
  .actions {
    display: flex;
    gap: 15px;
    justify-content: center;
  }
}
</style> 