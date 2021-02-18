<template>
    <div class='row justify-content-center p-4'>
        <h2> There are {{total_entries}} entries to donate </h2>
        <b-tabs pills content-class="mt-3" justified>
            <b-tab v-for="fileob in donations" :title="fileob.filename" :key="fileob.filename" lazy>
                <donation-table v-bind:filedata=fileob></donation-table>
            </b-tab>
        </b-tabs>
    </div>
</template>

<script>

import donationTable from './donationTable'

export default {
  components: { donationTable },
    props : {donations: Array},
    computed:{
        total_entries () {
            let total = 0
            this.donations.forEach(d=>total+=d.entries.length)
            return total
        }
    }

}
</script>