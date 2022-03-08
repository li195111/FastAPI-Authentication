import styles from '../../styles/Textarea.module.css'

function TextArea(props) {
    return (
        <div className={styles.textAreaBlock}>
            <label htmlFor={props.name}>{props.text}</label>
            <textarea className="w-full" name={props.name} id={props.id} cols="30" rows="10" readOnly></textarea>
        </div>
    )
}
export default TextArea