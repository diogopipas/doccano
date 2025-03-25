<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="headline">Dashboard Administrativo</v-card-title>
          <v-card-subtitle>Lista de Usuários</v-card-subtitle>
        </v-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            Usuários
            <v-spacer></v-spacer>
            <v-btn
              class="primary text-capitalize mr-2"
              @click="dialogCreate = true"
            >
              <v-icon left>{{ mdiAccountPlus }}</v-icon>
              Adicionar Usuário
            </v-btn>
            <v-text-field
              v-model="search"
              append-icon="mdi-magnify"
              label="Buscar"
              single-line
              hide-details
            ></v-text-field>
          </v-card-title>
          <v-card-text>
            <v-data-table
              :headers="userHeaders"
              :items="users"
              :items-per-page="10"
              :search="search"
              class="elevation-1"
              :footer-props="{
                'items-per-page-options': [10, 20, 50, 100],
                'items-per-page-text': 'Itens por página',
                'show-current-page': true,
                'show-first-last-page': true
              }"
            >
              <template #[`item.is_staff`]="{ item }">
                <v-chip
                  :color="item.is_staff ? 'primary' : 'grey'"
                  dark
                  small
                >
                  {{ item.is_staff ? 'Sim' : 'Não' }}
                </v-chip>
              </template>
              <template #[`item.date_joined`]="{ item }">
                {{ formatDate(item.date_joined) }}
              </template>
              <template #[`item.last_login`]="{ item }">
                {{ formatDate(item.last_login) }}
              </template>
              <template #[`item.actions`]="{ item }">
                <v-icon small class="mr-2" @click="editUser(item)">
                  {{ mdiPencil }}
                </v-icon>
                <v-icon small @click="confirmDelete(item)">
                  {{ mdiDelete }}
                </v-icon>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- Diálogo para criar novo usuário -->
    <v-dialog v-model="dialogCreate" max-width="500px">
      <v-card>
        <v-card-title class="headline">Adicionar Novo Usuário</v-card-title>
        <v-card-text>
          <v-form ref="form" v-model="validForm">
            <v-text-field
              v-model="newUser.username"
              :rules="[rules.required]"
              label="Nome de usuário"
              prepend-icon="mdi-account"
              required
            ></v-text-field>
            
            <v-text-field
              v-model="newUser.email"
              :rules="[rules.required, rules.email]"
              label="Email"
              prepend-icon="mdi-email"
              required
            ></v-text-field>
            
            <v-text-field
              v-model="newUser.password"
              :rules="[rules.required, rules.minLength]"
              label="Senha"
              prepend-icon="mdi-lock"
              type="password"
              required
            ></v-text-field>
            
            <v-text-field
              v-model="newUser.confirmPassword"
              :rules="[rules.required, rules.passwordMatch]"
              label="Confirmar Senha"
              prepend-icon="mdi-lock-check"
              type="password"
              required
            ></v-text-field>
            
            <v-switch
              v-model="newUser.is_staff"
              label="Administrador"
              color="primary"
            ></v-switch>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="dialogCreate = false">Cancelar</v-btn>
          <v-btn 
            color="primary" 
            text 
            :disabled="!validForm" 
            @click="createUser"
          >Salvar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Diálogo para confirmar exclusão de usuário -->
    <v-dialog v-model="dialogDelete" max-width="500px">
      <v-card>
        <v-card-title class="headline">Confirmar Exclusão</v-card-title>
        <v-card-text>
          Tem certeza que deseja excluir o usuário 
          <strong>{{ userToDelete ? userToDelete.username : '' }}</strong>?
          <br>
          Esta ação não pode ser desfeita.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="dialogDelete = false">Cancelar</v-btn>
          <v-btn 
            color="red darken-1" 
            text 
            @click="deleteUser"
          >Excluir</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Diálogo para editar usuário -->
    <v-dialog v-model="dialogEdit" max-width="500px">
      <v-card>
        <v-card-title class="headline">Editar Usuário</v-card-title>
        <v-card-text>
          <v-form ref="editForm" v-model="validEditForm">
            <v-text-field
              v-model="editedUser.username"
              :rules="[rules.required]"
              label="Nome de usuário"
              prepend-icon="mdi-account"
              required
            ></v-text-field>
            
            <v-text-field
              v-model="editedUser.email"
              :rules="[rules.required, rules.email]"
              label="Email"
              prepend-icon="mdi-email"
              required
              disabled
            ></v-text-field>
            
            <v-text-field
              v-model="editedUser.password"
              :rules="[editedUser.password ? passwordConfirmationRule : () => true]"
              label="Nova Senha (deixe em branco para manter a atual)"
              prepend-icon="mdi-lock"
              type="password"
            ></v-text-field>
            
            <v-text-field
              v-model="editedUser.confirmPassword"
              :rules="[editedUser.password ? passwordConfirmationRule : () => true]"
              label="Confirmar Nova Senha"
              prepend-icon="mdi-lock-check"
              type="password"
            ></v-text-field>
            
            <v-switch
              v-model="editedUser.is_staff"
              label="Administrador"
              color="primary"
            ></v-switch>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey darken-1" text @click="dialogEdit = false">Cancelar</v-btn>
          <v-btn 
            color="primary" 
            text 
            :disabled="!validEditForm" 
            @click="updateUser"
          >Salvar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import { mapGetters } from 'vuex'
import { mdiAccountGroup, mdiMagnify, mdiAccountPlus, mdiDelete, mdiPencil } from '@mdi/js'
import ApiService from '@/services/api.service'

export default {
  name: 'AdminDashboard',

  data() {
    return {
      mdiAccountGroup,
      mdiMagnify,
      mdiAccountPlus,
      mdiDelete,
      mdiPencil,
      search: '',
      dialogCreate: false,
      dialogDelete: false,
      dialogEdit: false,
      userToDelete: null,
      validForm: false,
      validEditForm: false,
      editedUser: {
        id: null,
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        is_staff: false
      },
      userHeaders: [
        { text: 'Nome de usuário', value: 'username', sortable: true },
        { text: 'Admin', value: 'is_staff', sortable: true },
        { text: 'Registrado em', value: 'date_joined', sortable: true },
        { text: 'Último login', value: 'last_login', sortable: true },
        { text: 'Email', value: 'email', sortable: true },
        { text: 'Ações', value: 'actions', sortable: false }
      ],
      passwordConfirmationRule: v =>
       v === this.editedUser.password || 'As senhas não coincidem',

      users: [],
      newUser: {
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        is_staff: false
      },
      rules: {
        required: v => !!v || 'Campo obrigatório',
        email: v => /.+@.+\..+/.test(v) || 'E-mail deve ser válido',
        minLength: v => !!v && v.length >= 8 || 'Senha deve ter pelo menos 8 caracteres',

      }
    }
  },

  computed: {
    ...mapGetters('auth', ['isAuthenticated', 'isStaff'])
  },

  async mounted() {
    if (this.isAuthenticated && this.isStaff) {
      await this.fetchUsers()
    }
  },

  methods: {
    async fetchUsers() {
      try {
        // Buscar usuários da API usando o repositório
        const response = await ApiService.get('/users')
        // Mapear os dados para garantir que email e último login sejam exibidos corretamente
        this.users = response.data.map(item => {
          return {
            id: item.id,
            username: item.username,
            is_staff: item.is_staff,
            is_superuser: item.is_superuser,
            email: item.email,
            date_joined: item.date_joined,
            last_login: item.last_login
          }
        })
      } catch (error) {
        console.error('Erro ao buscar usuários:', error)
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return 'Nunca'
      const date = new Date(dateString)
      return date.toLocaleDateString('pt-BR') + ' ' + date.toLocaleTimeString('pt-BR')
    },
    
    confirmDelete(user) {
      this.userToDelete = user
      this.dialogDelete = true
    },
    
    async deleteUser() {
      try {
        // Chamar a API para excluir o usuário
        const response = await ApiService.delete(`/users/delete/${this.userToDelete.id}/`);

        // Se a API não retornar JSON, assumimos sucesso
        let successMessage = "Usuário excluído com sucesso";
        // Verificar se response e response.data existem antes de acessar a propriedade success
        if (response && response.data && typeof response.data.success === 'string') {
          successMessage = response.data.success;
        }

        // Verificar se o método $toast existe antes de chamá-lo
        if (this.$toast && typeof this.$toast.success === 'function') {
          this.$toast.success(successMessage);
        } else {
          alert(successMessage);
        }
      } catch (error) {
        console.error("Erro ao excluir usuário:", error);

        // Se houver erro, captura a mensagem da API ou usa uma genérica
        let errorMessage = "Erro ao excluir usuário.";
        // Verificar error, error.response e error.response.data existem antes de acessar a error
        if (error && error.response && error.response.data && typeof error.response.data.error === 'string') {
          errorMessage = error.response.data.error;
        }

        // Verificar se o método $toast existe antes de chamá-lo
        if (this.$toast && typeof this.$toast.error === 'function') {
          this.$toast.error(errorMessage);
        } else {
          alert(errorMessage);
        }
      } finally {
        // Fechar o diálogo de exclusão
        this.dialogDelete = false;
        this.userToDelete = null;

        // Atualizar a lista de usuários
        await this.fetchUsers();
      }
    }

,

    async createUser() {
      if (!this.$refs.form.validate()) {
        return
      }
      
      try {
        // Preparar dados para a API
        const userData = {
          username: this.newUser.username,
          email: this.newUser.email,
          password1: this.newUser.password,
          password2: this.newUser.confirmPassword
        }
        
        // Chamar a API para criar o usuário
        await ApiService.post('/users/create', userData)
        
        // Atualizar a lista de usuários
        await this.fetchUsers()
        
        // Limpa o formulário
        this.resetForm()
        
        // Fecha o diálogo
        this.dialogCreate = false
        
        // Exibe uma mensagem de sucesso
        alert('Usuário criado com sucesso!')
      } catch (error) {
        console.error('Erro ao criar usuário:', error)
        alert('Erro ao criar usuário. Por favor, tente novamente.')
      }
    },
    
    resetForm() {
      this.newUser = {
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        is_staff: false
      }
      if (this.$refs.form) {
        this.$refs.form.reset()
      }
    },
    
    editUser(user) {
      this.editedUser = {
        id: user.id,
        username: user.username,
        email: user.email,
        password: '',
        confirmPassword: '',
        is_staff: user.is_staff
      }
      this.dialogEdit = true
    },
    
    async updateUser() {
      if (!this.$refs.editForm.validate()) {
        return
      }
      
      try {
        // Preparar dados para a API
        const userData = {
          username: this.editedUser.username,
          is_staff: this.editedUser.is_staff
        }
        
        // Adicionar senha apenas se foi fornecida
        if (this.editedUser.password) {
          userData.password1 = this.editedUser.password
          userData.password2 = this.editedUser.confirmPassword
        }
        
        // Chamar a API para atualizar o usuário
        await ApiService.put(`/users/update/${this.editedUser.id}`, userData)

        
        // Atualizar a lista de usuários
        await this.fetchUsers()
        
        // Fecha o diálogo
        this.dialogEdit = false
        
        // Exibe uma mensagem de sucesso
        alert('Usuário atualizado com sucesso!')
      } catch (error) {
        console.error('Erro ao atualizar usuário:', error)
        alert('Erro ao atualizar usuário. Por favor, tente novamente.')
      }
    }
  }
}
</script>