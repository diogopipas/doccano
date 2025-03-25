<template>
  <v-main>
    <admin-dashboard />
  </v-main>
</template>

<script>
import AdminDashboard from '@/components/admin/AdminDashboard'

export default {
  components: {
    AdminDashboard
  },
  
  middleware: ['check-auth', 'admin-only'],
  
  layout: 'default'
}
</script>