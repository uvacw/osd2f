<template>
<div>
    <div v-if="donations.length>0">
        <div class='row justify-content-center p-4'>
            <h2> {{content.file_indicator_text}} {{total_entries}}</h2>
        </div>

            <div class="row justify-content-center p-4">
                <b-row>
                    <b-col ><b-button size="lg" variant="success" @click="showConsentModal">{{ content.donate_button }}</b-button></b-col>
                    <b-col ><b-button size="sm" v-b-toggle.edit-donation variant="outline-primary"> {{ content.inspect_button }} </b-button></b-col>
                </b-row>
            </div>

        <div class="row justify-content-center p-4">
            <b-collapse id="edit-donation">
                <!-- actual inspection / remove interface -->
                <div class="row justify-content-center p-2">
                    <h4> {{ content.preview_component.title }} </h4>
                </div>
                <b-tabs  card-vertical content-class="mt-3" v-model="tabIndex" justified fill>
                    <b-tab :title=content.preview_component.title class="p-2"> 
                        <h5> {{ content.preview_component.title }} </h5>
                        <p v-for="p in content.preview_component.explanation">
                            {{p}}
                        </p>
                        </b-tab>
                    <b-tab v-for="fileob in donations" :title="fileob.filename" :key="fileob.filename" lazy>
                        <donation-table v-bind:filedata=fileob v-bind:content=content></donation-table>
                    </b-tab>
                </b-tabs>

                <div class="text-center">
                    <b-button-group class="mt-2">
                        <b-button variant="primary" @click="tabIndex--">{{content.preview_component.previous_file_button}}</b-button>
                        <b-button variant="primary" @click="tabIndex++">{{content.preview_component.next_file_button}}</b-button>
                    </b-button-group>
                </div>
                

            </b-collapse>
            <consent-confirmation :donations=this.donations :content=this.content></consent-confirmation>
        </div>
    </div>
</div>
</template>

<script>

import donationTable from './donationTable'
import consentConfirmation from './consentConfirmation'
import {server} from '../server_interaction.js'

export default {
  components: { donationTable,  consentConfirmation},
    props : {
        donations: Array,
        content: Object
        },
    updated : function(){
        server.log("INFO", "Tables shown changed", window.sid)
    },
    data() {
        return {
            tabIndex: 0
        }
    },
    computed:{
        total_entries () {
            let total = 0
            this.donations.forEach(d=>total+=d.entries.length)
            return total
        }
    },
    methods: {
        showConsentModal(){
            this.$bvModal.show('consent-modal')
            server.log("INFO", "Consent modal shown")
        }
    }

}
</script>