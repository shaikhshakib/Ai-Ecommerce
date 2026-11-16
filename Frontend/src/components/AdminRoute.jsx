import {Navigate} from 'react-router-dom'

function AdminRoute({children}) {
    const token = localStorage.getItem('access_token')
    const role = localStorage.getItem('user_role')


if(!token){
    return <Navigate to ="/login" replace />
}

if(role!=='admin') {
    return <Navigate to = "/" replace/>
}

return children
}
export default AdminRoute