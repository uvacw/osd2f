<template>
 <div>
     <h5> File to donate: {{ filedata.filename }} </h5>
    <span class="p-2">There are: <b> {{ this.rows }} </b> entries in this file selected for donation</span>
    <b-input-group>
        <b-form-input
            id="filter-input"
            v-model="filter"
            type="search"
            placeholder="Type to Search"
        ></b-form-input>

        <b-button
            variant="danger"
            @click="removeSelection"
            small
        >Remove selection</b-button>
    </b-input-group>

     <b-table 
        id="file-table"
        small
        responsive
        sticky-header="1200px"
        thClass="col-2"
        hover 
        selectable
        :items="items" 
        :fields="showfields" 
        :per-page="perPage" 
        :current-page="currentPage"
        :filter="filter"
        @row-selected="onRowSelected"
        @filtered="onFilterApply"
    >
    </b-table>
     <b-pagination 
        v-model="currentPage" 
        aria-controls="file-table"
        :total-rows="rows"
        :per-page="perPage"
    ></b-pagination>

</div>
</template>

<script>

export default {
    props: {
        fields: Array,
        filedata: Object,
    },
    // infer fields from entries
    created: function(){
        if (this.filedata.entries == undefined){return}
      var fields = new Set
      for (let i=0; i<this.filedata.entries.length; i++){
          fields.add(Object.keys(this.filedata.entries[i]))
      }
      this.showfields = Array(...fields)
    },
    data(){
        return {
            perPage: 15,
            currentPage: 1,
            filter: null,
            selected : null
        }
    },
    computed: {
        rows(){
         try {
             return this.filedata.entries.length
         } catch {
             console.log("no file yet")
             return 0
         }
        },
        items(){
            if (this.filedata.entries == undefined || this.filedata.entries==null){
                return []
            }
            
            return this.filedata.entries
        }
    },
    methods: {
        onRowSelected(items){
            this.selected = items
        },
        removeSelection(){
            if(this.selected==null){return}
            this.filedata.entries = this.filedata.entries.filter(e => !this.selected.includes(e))
            this.selected = null
        },
        onFilterApply(){
            this.currentPage = 1
        }
    }

}
</script>