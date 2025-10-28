/**
 * Configuração do PrimeVue com tema personalizado da Levitiis
 * Para páginas mais estilizadas e componentes avançados
 */

import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'
import DialogService from 'primevue/dialogservice'

// Importar ícones
import 'primeicons/primeicons.css'

// Componentes PrimeVue mais utilizados
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Textarea from 'primevue/textarea'
import Dropdown from 'primevue/dropdown'
import MultiSelect from 'primevue/multiselect'
import Calendar from 'primevue/calendar'
import Checkbox from 'primevue/checkbox'
import RadioButton from 'primevue/radiobutton'
import InputSwitch from 'primevue/inputswitch'
import Slider from 'primevue/slider'
import Rating from 'primevue/rating'
import ColorPicker from 'primevue/colorpicker'
import Knob from 'primevue/knob'
import Listbox from 'primevue/listbox'
import SelectButton from 'primevue/selectbutton'
import ToggleButton from 'primevue/togglebutton'
import SplitButton from 'primevue/splitbutton'
import SpeedDial from 'primevue/speeddial'

// Layout e Containers
import Panel from 'primevue/panel'
import Fieldset from 'primevue/fieldset'
import Card from 'primevue/card'
import Toolbar from 'primevue/toolbar'
import ScrollPanel from 'primevue/scrollpanel'
import Splitter from 'primevue/splitter'
import SplitterPanel from 'primevue/splitterpanel'

// Data
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import ColumnGroup from 'primevue/columngroup'
import Row from 'primevue/row'
import DataView from 'primevue/dataview'
import DataViewLayoutOptions from 'primevue/dataviewlayoutoptions'
import OrderList from 'primevue/orderlist'
import OrganizationChart from 'primevue/organizationchart'
import Paginator from 'primevue/paginator'
import PickList from 'primevue/picklist'
import Tree from 'primevue/tree'
import TreeSelect from 'primevue/treeselect'
import TreeTable from 'primevue/treetable'
import Timeline from 'primevue/timeline'

// Panel
import Accordion from 'primevue/accordion'
import AccordionTab from 'primevue/accordiontab'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import Divider from 'primevue/divider'

// Overlay
import Dialog from 'primevue/dialog'
import Sidebar from 'primevue/sidebar'
import Toast from 'primevue/toast'
import OverlayPanel from 'primevue/overlaypanel'
import ConfirmDialog from 'primevue/confirmdialog'
import ConfirmPopup from 'primevue/confirmpopup'
import DynamicDialog from 'primevue/dynamicdialog'

// File
import FileUpload from 'primevue/fileupload'

// Menu
import Menubar from 'primevue/menubar'
import Menu from 'primevue/menu'
import TieredMenu from 'primevue/tieredmenu'
import ContextMenu from 'primevue/contextmenu'
import MegaMenu from 'primevue/megamenu'
import PanelMenu from 'primevue/panelmenu'
import Steps from 'primevue/steps'
import TabMenu from 'primevue/tabmenu'
import Breadcrumb from 'primevue/breadcrumb'

// Chart (se necessário)
import Chart from 'primevue/chart'

// Messages
import Message from 'primevue/message'
import InlineMessage from 'primevue/inlinemessage'

// Media
import Carousel from 'primevue/carousel'
import Galleria from 'primevue/galleria'
import Image from 'primevue/image'

// Misc
import Avatar from 'primevue/avatar'
import AvatarGroup from 'primevue/avatargroup'
import Badge from 'primevue/badge'
import BlockUI from 'primevue/blockui'
import Chip from 'primevue/chip'
import Inplace from 'primevue/inplace'
import ProgressBar from 'primevue/progressbar'
import ProgressSpinner from 'primevue/progressspinner'
import ScrollTop from 'primevue/scrolltop'
import Skeleton from 'primevue/skeleton'
import Tag from 'primevue/tag'
import Terminal from 'primevue/terminal'

export function setupPrimeVue(app) {
  // Configurar PrimeVue
  app.use(PrimeVue, {
    ripple: true
  })
  
  // Serviços
  app.use(ToastService)
  app.use(ConfirmationService)
  app.use(DialogService)

  // Registrar componentes globalmente
  // Form
  app.component('PrimeButton', Button)
  app.component('PrimeInputText', InputText)
  app.component('PrimePassword', Password)
  app.component('PrimeTextarea', Textarea)
  app.component('PrimeDropdown', Dropdown)
  app.component('PrimeMultiSelect', MultiSelect)
  app.component('PrimeCalendar', Calendar)
  app.component('PrimeCheckbox', Checkbox)
  app.component('PrimeRadioButton', RadioButton)
  app.component('PrimeInputSwitch', InputSwitch)
  app.component('PrimeSlider', Slider)
  app.component('PrimeRating', Rating)
  app.component('PrimeColorPicker', ColorPicker)
  app.component('PrimeKnob', Knob)
  app.component('PrimeListbox', Listbox)
  app.component('PrimeSelectButton', SelectButton)
  app.component('PrimeToggleButton', ToggleButton)
  app.component('PrimeSplitButton', SplitButton)
  app.component('PrimeSpeedDial', SpeedDial)

  // Layout
  app.component('PrimePanel', Panel)
  app.component('PrimeFieldset', Fieldset)
  app.component('PrimeCard', Card)
  app.component('PrimeToolbar', Toolbar)
  app.component('PrimeScrollPanel', ScrollPanel)
  app.component('PrimeSplitter', Splitter)
  app.component('PrimeSplitterPanel', SplitterPanel)

  // Data
  app.component('PrimeDataTable', DataTable)
  app.component('PrimeColumn', Column)
  app.component('PrimeColumnGroup', ColumnGroup)
  app.component('PrimeRow', Row)
  app.component('PrimeDataView', DataView)
  app.component('PrimeDataViewLayoutOptions', DataViewLayoutOptions)
  app.component('PrimeOrderList', OrderList)
  app.component('PrimeOrganizationChart', OrganizationChart)
  app.component('PrimePaginator', Paginator)
  app.component('PrimePickList', PickList)
  app.component('PrimeTree', Tree)
  app.component('PrimeTreeSelect', TreeSelect)
  app.component('PrimeTreeTable', TreeTable)
  app.component('PrimeTimeline', Timeline)

  // Panel
  app.component('PrimeAccordion', Accordion)
  app.component('PrimeAccordionTab', AccordionTab)
  app.component('PrimeTabView', TabView)
  app.component('PrimeTabPanel', TabPanel)
  app.component('PrimeDivider', Divider)

  // Overlay
  app.component('PrimeDialog', Dialog)
  app.component('PrimeSidebar', Sidebar)
  app.component('PrimeToast', Toast)
  app.component('PrimeOverlayPanel', OverlayPanel)
  app.component('PrimeConfirmDialog', ConfirmDialog)
  app.component('PrimeConfirmPopup', ConfirmPopup)
  app.component('PrimeDynamicDialog', DynamicDialog)

  // File
  app.component('PrimeFileUpload', FileUpload)

  // Menu
  app.component('PrimeMenubar', Menubar)
  app.component('PrimeMenu', Menu)
  app.component('PrimeTieredMenu', TieredMenu)
  app.component('PrimeContextMenu', ContextMenu)
  app.component('PrimeMegaMenu', MegaMenu)
  app.component('PrimePanelMenu', PanelMenu)
  app.component('PrimeSteps', Steps)
  app.component('PrimeTabMenu', TabMenu)
  app.component('PrimeBreadcrumb', Breadcrumb)

  // Chart
  app.component('PrimeChart', Chart)

  // Messages
  app.component('PrimeMessage', Message)
  app.component('PrimeInlineMessage', InlineMessage)

  // Media
  app.component('PrimeCarousel', Carousel)
  app.component('PrimeGalleria', Galleria)
  app.component('PrimeImage', Image)

  // Misc
  app.component('PrimeAvatar', Avatar)
  app.component('PrimeAvatarGroup', AvatarGroup)
  app.component('PrimeBadge', Badge)
  app.component('PrimeBlockUI', BlockUI)
  app.component('PrimeChip', Chip)
  app.component('PrimeInplace', Inplace)
  app.component('PrimeProgressBar', ProgressBar)
  app.component('PrimeProgressSpinner', ProgressSpinner)
  app.component('PrimeScrollTop', ScrollTop)
  app.component('PrimeSkeleton', Skeleton)
  app.component('PrimeTag', Tag)
  app.component('PrimeTerminal', Terminal)
}

// Configuração de tema personalizado da Levitiis
export const levitiisThemeConfig = {
  primary: '#6366F1',
  primaryDark: '#4F46E5',
  secondary: '#8B5CF6',
  accent: '#06B6D4',
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6',
  surface: '#FFFFFF',
  background: '#FAFAFA'
}