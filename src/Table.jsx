import * as React from 'react';
import { DataGrid } from '@mui/x-data-grid';
import Paper from '@mui/material/Paper';
import WikiButton from './WikiButton';

// Table columns configuration
const columns = [
  { field: 'title', 
    headerName: 'Title', 
    width: 300, 
    headerAlign: 'center', 
  },
  { field: 'release_year', 
    headerName: 'Release Year', 
    width: 150, type: 'number', 
    headerAlign: 'center', 

    // Render year in order to not to be displayed as a number with decimal points
    renderCell: (params) => params.value?.toString().slice(0, 4) 
   },
  { field: 'country', 
    headerName: 'Country', 
    width: 200, 
    headerAlign: 'center', 
    align: 'center' 
  },
  { field: 'director', 
    headerName: 'Director', 
    width: 200, 
    headerAlign: 'center', 
    align: 'center' 
  },
  { field: 'box_office', 
    headerName: 'Box office ($)', 
    width: 200, 
    type: 'number', 
    headerAlign: 'center', 
    // Render box office in order to be displayed with commas
    renderCell: (params) => params.value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',') 
  },
  { 
    field: 'url', 
    headerName: 'URL', 
    width: 200,
    headerAlign: 'center', 
    // Render URL as a clickable button
    renderCell: (params) => <WikiButton url={params.value} />
  }
];

const paginationModel = { page: 0, pageSize: 100 };

export default function DataTable() {
    const [rows, setRows] = React.useState([]);

    // fethcing data from the server (self request)
    React.useEffect(() => {
        fetch('/S25-DWV-Assignment-1/films.json')
            .then((response) => response.json())
            .then((rows) => setRows(rows))
            .catch((error) => {
                console.error('Error:', error);
            });
    }, []);


  return (
    <>
    <h1> Films viewer  </h1>
    <Paper sx={{ height: 800, width: '100%' }}>
      <DataGrid
        rows={rows}
        columns={columns}
        getRowId={(row) => row.url}
        initialState={{ pagination: { paginationModel } }}
        pageSizeOptions={[10, 50, 100]}
        sx={{ border: 0 }}
      />
    </Paper>    
    </>
  );
}
