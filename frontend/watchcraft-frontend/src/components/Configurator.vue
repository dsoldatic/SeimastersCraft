<template>
  <div class="form-container">
    <img :src="`${baseImageURL}/logo.png`" alt="Seimasters Watches" class="logo" />

    <div class="watch-preview">
      <img v-if="selectedImages.strap" :src="`${baseImageURL}/strap/${selectedImages.strap}`" class="layer" alt="Strap" />
      <img v-if="selectedImages.case"  :src="`${baseImageURL}/case/${selectedImages.case}`"  class="layer" alt="Case" />
      <img v-if="selectedImages.dial"  :src="`${baseImageURL}/dial/${selectedImages.dial}`"  class="layer" alt="Dial" />
      <img v-if="selectedImages.hands" :src="`${baseImageURL}/hands/${selectedImages.hands}`" class="layer" alt="Hands" />
      <img v-if="selectedImages.box"   :src="`${baseImageURL}/box/${selectedImages.box}`"   class="layer box-layer" alt="Box" />
    </div>

    <h2>Konfiguriraj svoj sat</h2>
    <form @submit.prevent="submitOrder">
      <select v-model="form.case" required>
        <option disabled value="">Odaberi kućište</option>
        <option v-for="c in components.cases" :key="c.filename" :value="c.name">
          {{ c.name }} – {{ c.price }} €
        </option>
      </select>

      <select v-model="form.dial" required>
        <option disabled value="">Odaberi brojčanik</option>
        <option v-for="d in components.dials" :key="d.filename" :value="d.name">
          {{ d.name }} – {{ d.price }} €
        </option>
      </select>

      <select v-model="form.hands" required>
        <option disabled value="">Odaberi kazaljke</option>
        <option v-for="h in components.hands" :key="h.filename" :value="h.name">
          {{ h.name }} – {{ h.price }} €
        </option>
      </select>

      <select v-model="form.strap" required>
        <option disabled value="">Odaberi remen</option>
        <option v-for="s in components.straps" :key="s.filename" :value="s.name">
          {{ s.name }} – {{ s.price }} €
        </option>
      </select>

      <select v-model="form.box" required>
        <option disabled value="">Odaberi kutiju</option>
        <option v-for="b in components.boxes" :key="b.filename" :value="b.name">
          {{ b.name }} – {{ b.price }} €
        </option>
      </select>

      <input v-model="form.engraving"
             placeholder="Gravura (opcionalno - javimo Vam se email-om)" />
      <hr />

      <input v-model="form.customer_name"    placeholder="Ime" required />
      <input v-model="form.customer_surname" placeholder="Prezime" required />
      <input v-model="form.customer_email"    type="email" placeholder="Email" required />
      <input v-model="form.customer_phone"    placeholder="Broj mobitela" required />
      <input v-model="form.customer_address"  placeholder="Adresa" required />
      <input v-model="form.customer_city"     placeholder="Grad" required />
      <input v-model="form.customer_postcode" placeholder="Poštanski broj" required />

      <select v-model="form.payment_method" required>
        <option disabled value="">Način plaćanja</option>
        <option>Pouzećem</option>
        <option>Karticom (emailom dostavljamo podatke za plaćanje)</option>
      </select>

      <p><strong>Ukupna cijena:</strong> {{ totalPrice }} €</p>
      <button type="submit">Pošalji narudžbu</button>
    </form>
  </div>
</template>

<script>
export default {
  data() {
    return {
      baseImageURL: "https://seimasterscraft-production.up.railway.app/img",
      defaultForm: {
        case: "", dial: "", hands: "", strap: "", box: "",
        engraving: "",
        customer_name: "", customer_surname: "",
        customer_email: "", customer_phone: "",
        customer_address: "", customer_city: "", customer_postcode: "",
        payment_method: "", price: 0
      },
      form: {},
      components: { cases: [], dials: [], hands: [], straps: [], boxes: [] },
      selectedImages: { case: "", dial: "", hands: "", strap: "", box: "" },
      totalPrice: 0
    };
  },
  methods: {
    resetForm() {
      this.form = { ...this.defaultForm };
      this.totalPrice = 0;
      this.selectedImages = { case: "", dial: "", hands: "", strap: "", box: "" };
    },
    async fetchComponents() {
      const api = import.meta.env.VITE_API_URL;
      const map = { case: "cases", dial: "dials", hands: "hands", strap: "straps", box: "boxes" };
      for (const type in map) {
        try {
          const res = await fetch(`${api}/image-components?type=${type}`);
          this.components[map[type]] = res.ok ? await res.json() : [];
        } catch {
          this.components[map[type]] = [];
        }
      }
    },
    calculatePrice() {
      let sum = 0;
      const map = { case: "cases", dial: "dials", hands: "hands", strap: "straps", box: "boxes" };
      for (const key in map) {
        const item = this.components[map[key]].find(x => x.name === this.form[key]);
        if (item) sum += item.price;
      }
      this.totalPrice = sum;
      this.form.price = sum;
    },
    async submitOrder() {
      this.calculatePrice();
      const api = import.meta.env.VITE_API_URL;
      const res = await fetch(`${api}/order`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(this.form)
      });
      const data = await res.json();
      alert(data.message);
      this.resetForm();
    },
setImage(type, name) {
  const map = { case: "cases", dial: "dials", hands: "hands", strap: "straps", box: "boxes" };
  const item = this.components[map[type]].find(
    x => x.name.trim().toLowerCase() === name.trim().toLowerCase()
  );
  console.log(`[SET IMAGE] ${type}:`, name, '->', item?.filename); // debug
  this.selectedImages[type] = item ? item.filename : "";
}
  },
  watch: {
    "form.case"(v)  { this.calculatePrice(); this.setImage("case", v); },
    "form.dial"(v)  { this.calculatePrice(); this.setImage("dial", v); },
    "form.hands"(v) { this.calculatePrice(); this.setImage("hands", v); },
    "form.strap"(v) { this.calculatePrice(); this.setImage("strap", v); },
    "form.box"(v)   { this.calculatePrice(); this.setImage("box", v); }
  },
  async mounted() {
    this.resetForm();
    await this.fetchComponents();
  }
};
</script>

<style>
.form-container {
  position: relative;
  max-width: 600px;
  margin: auto;
  padding: 2rem;
  background: #f4f4f4;
  border-radius: 12px;
}
.logo {
  position: absolute;
  top: 10px;
  left: 10px;
  width: 120px;
  z-index: 10;
  pointer-events: none;
}
input, select {
  display: block;
  width: 100%;
  margin-bottom: 1rem;
  padding: 0.5rem;
}
button {
  padding: 0.7rem;
  width: 100%;
  background: #1976d2;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
}
.watch-preview {
  position: relative;
  width: 300px;
  height: 300px;
  margin: 1rem auto;
}
.layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
}
.layer.box-layer {
  top: 90%;
  left: 120%;
  width: 50%;
  transform: translate(-50%, -50%);
}
</style>