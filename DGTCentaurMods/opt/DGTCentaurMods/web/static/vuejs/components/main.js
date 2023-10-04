import { ref } from 'vue'
export default {
  setup() {
    const id = "Alistair-Centaur-Mods"
    return { id }
  },
  template: `
  
  <h2>{{id}}</h2>
  <div>New web is coming!</div>

`
}