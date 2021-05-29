<template>
    <div>
        <b-modal 
            :title="content.consent_popup.title"
            id="consent-modal" 
            :ok-title="content.consent_popup.accept_button"
            ok-variant="success"
            :cancel-title="content.consent_popup.decline_button"
            :ok-disabled="this.processing"
            @ok="sub"
        >
            <b-overlay :show="show" rounded="sm">
                <div :aria-hidden="show ? 'true' : null">
                    <div class="p-1"> {{ content.consent_popup.lead }} </div>
                    <ul>
                        <li v-for="lit in content.consent_popup.points"> {{lit}} </li>
                    </ul>

                    <div class="p-1"> {{ content.consent_popup.end_text }} </div>
                </div>
            </b-overlay>
        </b-modal>
    </div>
</template>
<script>
import {server} from "../server_interaction"

export default {
    props:{
        donations : Array,
        content: Object
    },
    data(){
        return {
            show: false,
            processing : false
            }
    },
    computed: {
        n_entries() {
            let total = 0
            this.donations.forEach(d=>total+=d.entries.length)
            return total
        }
    },
    methods:{
        sub(evt){
            evt.preventDefault()
            this.show = true
            this.processing = true

            server.log("INFO", "consent given, uploading file")

            fetch('/upload', {
                method: 'POST',
                mode: 'same-origin',
                credentials: 'same-origin',
                headers: {
                'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.donations)
            })
            .then(() => {
            // remove processing queue
                this.processing = false
                noDonationYet = false
                this.show = false
                this.$bvModal.hide("consent-modal")
                this.$parent.$parent.donations = []
                document.getElementById('thankyou').classList.remove('invisible')
            })
            .catch(error => {
            console.log('Error', error)
            server.log("ERROR", "failed to upload file")
            })

        }
    }

}
</script>