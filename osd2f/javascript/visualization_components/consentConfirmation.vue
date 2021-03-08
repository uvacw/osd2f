<template>
    <div>
        <b-modal 
            title="I want to donate my data..." 
            id="consent-modal" 
            ok-title="I consent" 
            ok-variant="success"
            cancel-title="I'm sorry"
            :ok-disabled="this.processing"
            @ok="sub"
        >
            <b-overlay :show="show" rounded="sm">
                <div :aria-hidden="show ? 'true' : null">
                    Thank you for considering to donate your data to this project. 

                    Please understand the following:
                    <ul>
                        <li> Your data will be kept until 5 years after publishing the results of this project </li>
                        <li> You data will <b>never</b> be shared with third parties </li> 
                        <li> etcetera.... </li>
                    </ul>

                    Do you want to donate {{n_entries}} entries? 
                </div>
            </b-overlay>
        </b-modal>
    </div>
</template>
<script>

export default {
    props:{
        donations : Array
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
            })

        }
    }

}
</script>