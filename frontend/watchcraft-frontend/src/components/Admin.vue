<template>
  <div class="admin-container">
    <h2>Pregled svih narudžbi</h2>
    <ul v-if="orders.length">
      <li v-for="order in orders" :key="order.id">
        <strong>{{ order.customer_name }} {{ order.customer_surname }}</strong> –
        {{ order.case }} / {{ order.dial }} / {{ order.strap }} –
        {{ order.created_at }} –
        {{ order.payment_method }}
      </li>
    </ul>
    <p v-else>Nema narudžbi.</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      orders: [],
    };
  },
  async mounted() {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/orders`);
    this.orders = await res.json();
  }
};
</script>

<style>
.admin-container {
  max-width: 700px;
  margin: auto;
  padding: 2rem;
}
li {
  margin-bottom: 1rem;
  padding: 1rem;
  background: #eee;
  border-radius: 6px;
}
</style>