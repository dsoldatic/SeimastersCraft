<template>
  <div class="admin-container">
    <h2>Pregled svih narudžbi</h2>
    <table v-if="orders.length">
      <thead>
        <tr>
          <th>ID</th>
          <th>Kućište</th>
          <th>Brojčanik</th>
          <th>Kazaljke</th>
          <th>Remen</th>
          <th>Kutija</th>
          <th>Gravura</th>
          <th>Ime i Prezime</th>
          <th>Email</th>
          <th>Mobitel</th>
          <th>Adresa</th>
          <th>Grad</th>
          <th>Poštanski broj</th>
          <th>Plaćanje</th>
          <th>Vrijeme</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="order in orders" :key="order.id">
          <td>{{ order.id }}</td>
          <td>{{ order.case }}</td>
          <td>{{ order.dial }}</td>
          <td>{{ order.hands }}</td>
          <td>{{ order.strap }}</td>
          <td>{{ order.box }}</td>
          <td>{{ order.engraving || '—' }}</td>
          <td>{{ order.customer_name }} {{ order.customer_surname }}</td>
          <td>{{ order.customer_email }}</td>
          <td>{{ order.customer_phone }}</td>
          <td>{{ order.customer_address }}</td>
          <td>{{ order.customer_city }}</td>
          <td>{{ order.customer_postcode }}</td>
          <td>{{ order.payment_method }}</td>
          <td>{{ new Date(order.created_at).toLocaleString() }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else>Učitavanje narudžbi...</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      orders: []
    }
  },
  async mounted() {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/admin/configurations`);
    this.orders = await res.json();
  }
}
</script>

<style>
.admin-container {
  max-width: 95%;
  margin: auto;
  padding: 2rem;
  background: #f9f9f9;
  border-radius: 12px;
}
table {
  width: 100%;
  border-collapse: collapse;
}
thead {
  background: #1976d2;
  color: white;
}
td, th {
  padding: 0.5rem;
  border: 1px solid #ccc;
  text-align: left;
}
tbody tr:nth-child(even) {
  background-color: #f2f2f2;
}
</style>