export default function ({ store, redirect }) {
  if (!store.getters['auth/isAuthenticated']) {
    return redirect('/auth')
  }
  
  if (!store.getters['auth/isStaff']) {
    return redirect('/projects')
  }
}