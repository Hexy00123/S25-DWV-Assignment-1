import * as React from 'react';
import { DataGrid } from '@mui/x-data-grid';
import Paper from '@mui/material/Paper';
import WikiButton from './WikiButton';

const columns = [
//   { field: 'id', headerName: 'ID', width: 70 },
//   { field: 'firstName', headerName: 'First name', width: 160 },
//   { field: 'lastName', headerName: 'Last name', width: 160 },
//   {
//     field: 'age',
//     headerName: 'Age',
//     type: 'number',
//     width: 120,
//   },
//   {
//     field: 'fullName',
//     headerName: 'Full name',
//     description: 'This column has a value getter and is not sortable.',
//     sortable: false,
//     width: 160,
//     valueGetter: (value, row) => `${row.firstName || ''} ${row.lastName || ''}`,
//   },

    // { field: 'id', headerName: 'ID', width: 200 },
    { field: 'title', headerName: 'Title', width: 200 },
    { field: 'release_year', headerName: 'Release Year', width: 150 },
    { field: 'country', headerName: 'Country', width: 200 },
    { field: 'director', headerName: 'Director', width: 200 },  
    { field: 'box_office', headerName: 'Box office ($)', width: 200, type: 'number'},
    { 
        field: 'url', 
        headerName: 'URL', 
        width: 200,
        renderCell: (params) => <WikiButton url={params.value} />
    }
];



const paginationModel = { page: 0, pageSize: 100 };

export default function DataTable() {
    const [rows, setRows] = React.useState([]);

    React.useEffect(() => {
        fetch('/films.json')
            .then((response) => response.json())
            .then((rows) => setRows(rows))
            .catch((error) => {
                console.error('Error:', error);
            });
    }, []);


  return (
    <>
    Total docs: {rows.length}
    <Paper sx={{ height: 800, width: '100%' }}>
      <DataGrid
        rows={rows}
        columns={columns}
        getRowId={(row) => row.url}
        initialState={{ pagination: { paginationModel } }}
        pageSizeOptions={[10, 50, 100]}
        // checkboxSelection
        sx={{ border: 0 }}
      />
    </Paper>    
    {/* <WikiButton/> */}
    </>
  );
}
