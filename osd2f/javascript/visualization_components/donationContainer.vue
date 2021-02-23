<template>
<div>
    <div v-if="donations.length>0">
        <div class='row justify-content-center p-4'>
            <h2> There are {{total_entries}} entries to donate </h2>
        </div>

            <div class="row justify-content-center p-4">
                <b-row>
                    <b-col ><b-button size="lg" variant="success" v-b-modal.consent-modal>Donate!</b-button></b-col>
                    <b-col ><b-button size="sm" v-b-toggle.edit-donation variant="outline-primary"> Inspect & edit your donation </b-button></b-col>
                </b-row>
            </div>

        <div class="row justify-content-center p-4">
            <b-collapse id="edit-donation">
                <!-- actual inspection / remove interface -->
                <div class="row justify-content-center p-2">
                    <h4> Select files to inspect & edit your donation </h4>
                </div>
                <b-tabs  card-vertical content-class="mt-3" v-model="tabIndex" justified fill>
                    <b-tab title="Inspect & Edit your donation" class="p-2"> 
                        <h5> Select a file to inspect what you will be donating </h5>
                        <p> At the top you will see the files that are part of your upload</p>
                        <p> In each of these files, you can see the individual entries you will be donating </p>
                        <p> Have a look at the entries and remove things you would not like to donate by clicking on the rows and pressing 'remove selection' </p>
                        </b-tab>
                    <b-tab v-for="fileob in donations" :title="fileob.filename" :key="fileob.filename" lazy>
                        <donation-table v-bind:filedata=fileob></donation-table>
                    </b-tab>
                </b-tabs>

                <div class="text-center">
                    <b-button-group class="mt-2">
                        <b-button variant="primary" @click="tabIndex--">Previous file</b-button>
                        <b-button variant="primary" @click="tabIndex++">Next file</b-button>
                    </b-button-group>
                </div>
                

            </b-collapse>
            <consent-confirmation :donations=this.donations></consent-confirmation>
        </div>
    </div>
</div>
</template>

<script>

import donationTable from './donationTable'
import consentConfirmation from './consentConfirmation'


export default {
  components: { donationTable,  consentConfirmation},
    props : {
        donations: Array
        },
    data() {
        return {
            tabIndex: 1
        }
    },
    computed:{
        total_entries () {
            let total = 0
            this.donations.forEach(d=>total+=d.entries.length)
            return total
        }
    }

}
</script>