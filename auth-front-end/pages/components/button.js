import styles from '../../styles/Btn.module.css'

function Btn(props) {
    return (
        <button className={`${styles.btn} m-tb-10 btn-std`} id={props.id} onClick={props.onclick}>{props.text}</button>
    )
}
export default Btn