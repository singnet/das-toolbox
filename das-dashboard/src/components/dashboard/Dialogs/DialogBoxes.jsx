import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from "@mui/material";


export function ConfirmDialog({ dialogOpen, setDialogOpen, message, action }){

    return (
        <>
            <Dialog open = {dialogOpen}>
                <DialogTitle>Confirm action</DialogTitle>
                <DialogContent>
                    <DialogContentText>{message}</DialogContentText>
                    <DialogActions>
                        <Button onClick={() => action()}>Confirm</Button>
                        <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
                    </DialogActions>
                </DialogContent>
            </Dialog>
        </>
    )

}