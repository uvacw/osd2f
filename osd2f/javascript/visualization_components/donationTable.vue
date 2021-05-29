<template>
 <div>
     <h5> File: {{ filedata.filename }} </h5>

    <span>{{content.preview_component.entries_in_file_text}} <b> {{ this.rows }} </b></span>
    
    <div class="row">
        <b-input-group :prepend="content.preview_component.search_prompt" class="mt-3">
            
            <b-form-input
                id="filter-input"
                v-model="filter"
                type="search"
                :placeholder="content.preview_component.search_box_placeholder"
            ></b-form-input>

            <b-input-group-append>
                <b-button
                    variant="danger"
                    @click="removeSelection"
                    small
                >{{content.preview_component.remove_rows_button}}</b-button>
            </b-input-group-append>
        </b-input-group>
    </div>
    <div class="row">
        <div class="col-10">
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
        </div>
    </div>

    <b-pagination 
        v-model="currentPage" 
        aria-controls="file-table"
        :total-rows="rows"
        :per-page="perPage"
    ></b-pagination>


</div>
</template>

<script>
import {server} from '../server_interaction'
export default {
    props: {
        fields: Array,
        filedata: Object,
        content: Object
    },
    // infer fields from entries
    created: function(){
        if (this.filedata.entries == undefined){return}
      var fields = new Set
      for (let i=0; i<this.filedata.entries.length; i++){
          Object.keys(this.filedata.entries[i]).forEach((f)=>fields.add(f))
      }
      let showfields = new Array
      fields.forEach(f => {
          let o = new Object
          o[f] = { 
              "label": f, 
              "tdClass":"colClass",
              "sortable" : true
              } 
          showfields.push(o)}
          )
      
      this.showfields = showfields
    },
    data(){
        return {
            perPage: 5,
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
            if (items.length>0){server.log("INFO","select row", this.filedata.submission_id)}
            this.selected = items
        },
        removeSelection(){
            if(this.selected==null){return}
            server.log("INFO",`removed rows`, window.sid, {rows_removed:this.selected.length})
            this.filedata.n_deleted += this.selected.length
            this.filedata.entries = this.filedata.entries.filter(e => !this.selected.includes(e))
            this.selected = null
        },
        onFilterApply(){
            this.currentPage = 1
        }
    }

}
</script>